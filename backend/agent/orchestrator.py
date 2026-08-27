"""
SafeRemitAgent — the AI agent orchestration layer.

Built on LangGraph (github.com/langchain-ai/langgraph — listed in the
hackathon's AI Resource & Tooling Guide, section 2, "Code-first agent
frameworks"). LangGraph models the agent as a directed graph of nodes and
conditional edges, which maps onto how this agent actually behaves: it is
NOT a fixed pipeline that calls every CAMARA API on every request. It
works like a fraud analyst — cheap checks first, deeper (slower) signals
only when the transaction is sensitive or an early signal looks wrong,
then an LLM analyst weighs the combination.

Graph:

    initial_checks ──[escalate?]──> escalated_checks ──> ai_assessment ──> finalize
       (number verification            (device status +      (Gemini reads the       (reconcile
        + SIM swap, parallel)            location, parallel)   signal combination)     rules + AI)
                       │                                                                    │
                       └───────────── fast path (clean login) ──────────────────────────────┘

Within a node the independent CAMARA calls run concurrently. The LLM step
runs only on the escalation path — a clean login has no concerning
combination to reason about, so it stays fast.

`finalize` reconciles two opinions: the transparent rules score
(scoring.py) and Gemini's verdict (assessment.py). It takes the stricter
decision and flags any disagreement for human review. If Gemini is
unconfigured or the call fails, the rules score stands alone — the demo
never depends on the LLM.
"""
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from . import assessment
from .rationale import explain
from .scoring import (
    decision_for_score,
    score_device_status,
    score_location_verification,
    score_number_verification,
    score_sim_swap,
)
from ..camara_apis.device_status import DeviceStatusClient
from ..camara_apis.location_verification import LocationVerificationClient
from ..camara_apis.number_verification import NumberVerificationClient
from ..camara_apis.sim_swap import SimSwapClient

SENSITIVE_ACTIONS = {"onboarding", "transfer"}
_SEVERITY = {"ALLOW": 0, "STEP_UP": 1, "BLOCK": 2}

_sim_swap_client = SimSwapClient()
_number_verification_client = NumberVerificationClient()
_device_status_client = DeviceStatusClient()
_location_verification_client = LocationVerificationClient()


class AgentState(TypedDict):
    phone_number: str
    action_type: str
    device_fingerprint: str
    claimed_location: str
    scenario: str
    score: int
    trace: List[Dict[str, Any]]
    escalate: bool
    ai: Optional[Dict[str, Any]]
    ai_ran: bool
    result: Optional[Dict[str, Any]]


def _entry(step: str, api: Optional[str], signal, points: int, reason: str, running: int) -> dict:
    return {"step": step, "api": api, "signal": signal,
            "points": points, "reason": reason, "running_score": running}


def node_initial_checks(state: AgentState) -> dict:
    """Number Verification + SIM Swap — the cheap, always-run checks. They
    only need the phone number, so they run concurrently."""
    with ThreadPoolExecutor(max_workers=2) as pool:
        f_nv = pool.submit(_number_verification_client.verify,
                           state["phone_number"], scenario=state["scenario"])
        f_ss = pool.submit(_sim_swap_client.check,
                           state["phone_number"], scenario=state["scenario"])
        nv, ss = f_nv.result(), f_ss.result()

    score = state["score"]
    trace = list(state["trace"])

    nv_points, nv_reason = score_number_verification(nv)
    score += nv_points
    trace.append(_entry("number_verification", "number_verification", nv, nv_points, nv_reason, score))

    ss_points, ss_reason = score_sim_swap(ss)
    score += ss_points
    trace.append(_entry("sim_swap", "sim_swap", ss, ss_points, ss_reason, score))

    early_flag = ss["swapped"] or not nv["verified"]
    sensitive = state["action_type"] in SENSITIVE_ACTIONS
    escalate = bool(early_flag or sensitive)

    if sensitive and early_flag:
        note = "sensitive action AND an early suspicious signal"
    elif sensitive:
        note = "sensitive action type"
    elif early_flag:
        note = "early signal already suspicious"
    else:
        note = None

    if note:
        trace.append(_entry("escalation_decision", None, None, 0,
                            f"Escalating to device + location checks ({note}).", score))
    else:
        trace.append(_entry("escalation_decision", None, None, 0,
                            "Routine login, clean early signals — skipping device/location checks (fast path).", score))

    return {"score": score, "trace": trace, "escalate": escalate}


def route_after_initial(state: AgentState) -> str:
    return "escalate" if state["escalate"] else "fast_path"


def node_escalated_checks(state: AgentState) -> dict:
    """Device Status + Location Verification — the deeper signals, pulled
    only when the agent decided to escalate. Independent, so concurrent."""
    with ThreadPoolExecutor(max_workers=2) as pool:
        f_ds = pool.submit(_device_status_client.check, state["phone_number"],
                           state["device_fingerprint"], scenario=state["scenario"])
        f_lv = pool.submit(_location_verification_client.verify, state["phone_number"],
                           state["claimed_location"], scenario=state["scenario"])
        ds, lv = f_ds.result(), f_lv.result()

    score = state["score"]
    trace = list(state["trace"])

    ds_points, ds_reason = score_device_status(ds)
    score += ds_points
    trace.append(_entry("device_status", "device_status", ds, ds_points, ds_reason, score))

    lv_points, lv_reason = score_location_verification(lv)
    score += lv_points
    trace.append(_entry("location_verification", "location_verification", lv, lv_points, lv_reason, score))

    return {"score": score, "trace": trace}


def node_ai_assessment(state: AgentState) -> dict:
    """LLM analyst: hand Gemini the signal combination and ask for a
    verdict. Only runs on the escalation path — a clean login has no
    concerning combination to reason about. Returns None (recorded as
    such) when unconfigured or on failure; finalize() then uses the
    rules score alone."""
    trace = list(state["trace"])
    if not assessment.available():
        return {"ai": None, "ai_ran": True, "trace": trace}

    ai = assessment.assess(state["action_type"], state["trace"])
    if ai:
        trace.append(_entry(
            "ai_assessment", None, {"source": "gemini", **ai}, 0,
            f"AI analyst: {ai['decision'].replace('_', '-')} (risk {ai['risk_score']}) — {ai['reasoning']}",
            state["score"],
        ))
    else:
        trace.append(_entry("ai_assessment", None, {"source": "gemini-unavailable"}, 0,
                            "AI analyst call did not return a verdict — proceeding on the rules score.",
                            state["score"]))
    return {"ai": ai, "ai_ran": True, "trace": trace}


def node_finalize(state: AgentState) -> dict:
    rules_score = min(100, state["score"])
    rules_decision = decision_for_score(state["score"])
    ai = state.get("ai")

    if ai:
        final_decision = max(rules_decision, ai["decision"], key=lambda d: _SEVERITY[d])
        agreement = rules_decision == ai["decision"]
        risk_score = rules_score if agreement else max(rules_score, ai["risk_score"])
    else:
        final_decision = rules_decision
        agreement = None
        risk_score = rules_score

    rationale = explain(final_decision, risk_score, state["trace"],
                        ai=ai, agreement=agreement, rules_decision=rules_decision)

    signal_sources = sorted({
        s["signal"]["source"]
        for s in state["trace"]
        if s.get("signal") and "source" in s["signal"]
    })

    if ai:
        mode = "gemini + rules"
    elif not state.get("ai_ran"):
        mode = "rules only (fast path — no escalation)"
    elif assessment.available():
        mode = "rules only (AI analyst call failed)"
    else:
        mode = "rules only"

    result = {
        "decision": final_decision,
        "risk_score": risk_score,
        "raw_score": state["score"],
        "apis_called": [s["api"] for s in state["trace"] if s["api"]],
        "camara_mode": "live" if "live" in signal_sources else "mock",
        "signal_sources": signal_sources,
        "assessment": {
            "mode": mode,
            "rules": {"decision": rules_decision, "risk_score": rules_score},
            "ai": ai,
            "agreement": agreement,
        },
        "rationale": rationale["text"],
        "rationale_source": rationale["source"],
        "trace": state["trace"],
    }
    return {"result": result}


def _build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("initial_checks", node_initial_checks)
    graph.add_node("escalated_checks", node_escalated_checks)
    graph.add_node("ai_assessment", node_ai_assessment)
    graph.add_node("finalize", node_finalize)

    graph.set_entry_point("initial_checks")
    graph.add_conditional_edges("initial_checks", route_after_initial, {
        "escalate": "escalated_checks",
        "fast_path": "finalize",
    })
    graph.add_edge("escalated_checks", "ai_assessment")
    graph.add_edge("ai_assessment", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile()


_compiled_graph = _build_graph()


class SafeRemitAgent:
    """Thin, stable wrapper around the compiled LangGraph so app.py doesn't
    need to know anything about graph internals."""

    def decide(self, request: dict, scenario: str = "clean") -> dict:
        initial_state: AgentState = {
            "phone_number": request["phone_number"],
            "action_type": request.get("action_type", "login"),
            "device_fingerprint": request.get("device_fingerprint", "unknown-device"),
            "claimed_location": request.get("claimed_location", "unspecified"),
            "scenario": scenario,
            "score": 0,
            "trace": [],
            "escalate": False,
            "ai": None,
            "ai_ran": False,
            "result": None,
        }
        final_state = _compiled_graph.invoke(initial_state)
        return final_state["result"]
