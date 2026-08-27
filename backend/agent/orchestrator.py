"""
SafeRemitAgent — the AI agent orchestration layer.

Built on LangGraph (github.com/langchain-ai/langgraph — listed in the
hackathon's AI Resource & Tooling Guide, section 2, "Code-first agent
frameworks"). LangGraph models the agent as a directed graph of nodes and
conditional edges, which maps directly onto how this agent actually
behaves: it is NOT a fixed pipeline that calls all four CAMARA APIs on
every request. It behaves like a fraud analyst would — cheap, low-risk
checks first, escalating to deeper signals only when the transaction is
sensitive or an early signal already looks wrong. That's what the Guide's
own tip means by "agentic": the agent decides which CAMARA API to call
next, it isn't just a button the user presses.

Graph:

    initial_checks ──[conditional]──> escalated_checks ──> finalize
       (number verification            (device status +          │
        + SIM swap, in parallel)        location, in parallel)    │
                       │                                          │
                       └────── fast path (clean login) ───────────┘

Within a node the independent CAMARA calls run concurrently — same
signals, roughly half the wall-clock latency, which matters when each
call is a real round trip to the operator network.

Escalation triggers when:
  - the action itself is sensitive (onboarding / transfer), or
  - an early signal already looks wrong (SIM swap flagged, or the number
    failed carrier verification).

`finalize` fuses every signal actually pulled into a 0-100 risk score
with a running trace, maps it to ALLOW / STEP_UP / BLOCK, and calls the
rationale generator (Gemini, per the Guide's "Hosted APIs with a free
tier" list, with an automatic deterministic fallback — see rationale.py).
"""
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

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


def node_finalize(state: AgentState) -> dict:
    decision = decision_for_score(state["score"])
    rationale = explain(decision, state["score"], state["trace"])
    signal_sources = sorted({
        s["signal"]["source"]
        for s in state["trace"]
        if s.get("signal") and "source" in s["signal"]
    })
    result = {
        "decision": decision,
        "risk_score": min(100, state["score"]),
        "raw_score": state["score"],
        "apis_called": [s["api"] for s in state["trace"] if s["api"]],
        "camara_mode": "live" if "live" in signal_sources else "mock",
        "signal_sources": signal_sources,
        "rationale": rationale["text"],
        "rationale_source": rationale["source"],
        "trace": state["trace"],
    }
    return {"result": result}


def _build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("initial_checks", node_initial_checks)
    graph.add_node("escalated_checks", node_escalated_checks)
    graph.add_node("finalize", node_finalize)

    graph.set_entry_point("initial_checks")
    graph.add_conditional_edges("initial_checks", route_after_initial, {
        "escalate": "escalated_checks",
        "fast_path": "finalize",
    })
    graph.add_edge("escalated_checks", "finalize")
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
            "result": None,
        }
        final_state = _compiled_graph.invoke(initial_state)
        return final_state["result"]
