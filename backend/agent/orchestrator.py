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
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, List, Optional, Tuple, TypedDict

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

_log = logging.getLogger("saferemit.agent")

_sim_swap_client = SimSwapClient()
_number_verification_client = NumberVerificationClient()
_device_status_client = DeviceStatusClient()
_location_verification_client = LocationVerificationClient()


def _run_parallel(t0: float, jobs: List[Tuple[str, Callable[[], Any]]]) -> Dict[str, Tuple[Any, int, int]]:
    """Run the CAMARA calls in `jobs` concurrently. Returns
    {api_name: (result, start_ms, end_ms)} with timings measured from `t0`
    (the graph's entry perf_counter) so the response can *show* that the
    independent calls overlapped — real proof of parallel API activity.

    Each call is logged with its worker thread id; interleaved thread ids
    with overlapping start/end windows in the Render logs are the same
    proof, seen from the server side.
    """
    def timed(name: str, fn: Callable[[], Any]) -> Tuple[Any, int, int]:
        start = round((time.perf_counter() - t0) * 1000)
        _log.info("CAMARA %-22s  start=%5dms  thread=%s  -> calling", name, start, threading.get_ident())
        result = fn()
        end = round((time.perf_counter() - t0) * 1000)
        src = result.get("source", "?") if isinstance(result, dict) else "?"
        _log.info("CAMARA %-22s  start=%5dms  end=%5dms  (%4dms)  thread=%s  source=%s",
                  name, start, end, end - start, threading.get_ident(), src)
        return result, start, end

    with ThreadPoolExecutor(max_workers=max(2, len(jobs))) as pool:
        futures = {name: pool.submit(timed, name, fn) for name, fn in jobs}
        return {name: fut.result() for name, fut in futures.items()}


class AgentState(TypedDict):
    phone_number: str
    action_type: str
    device_fingerprint: str
    claimed_location: str
    scenario: str
    t0: float
    score: int
    trace: List[Dict[str, Any]]
    escalate: bool
    ai: Optional[Dict[str, Any]]
    ai_ran: bool
    result: Optional[Dict[str, Any]]


def _entry(step: str, api: Optional[str], signal, points: int, reason: str, running: int,
           timing: Optional[Tuple[int, int]] = None) -> dict:
    e = {"step": step, "api": api, "signal": signal,
         "points": points, "reason": reason, "running_score": running}
    if timing is not None:
        e["timing"] = {"start_ms": timing[0], "end_ms": timing[1]}
    return e


def node_initial_checks(state: AgentState) -> dict:
    """Number Verification + SIM Swap — the cheap, always-run checks. They
    only need the phone number, so they run concurrently."""
    pn, sc = state["phone_number"], state["scenario"]
    out = _run_parallel(state["t0"], [
        ("number_verification", lambda: _number_verification_client.verify(pn, scenario=sc)),
        ("sim_swap", lambda: _sim_swap_client.check(pn, scenario=sc)),
    ])
    (nv, nv_s, nv_e), (ss, ss_s, ss_e) = out["number_verification"], out["sim_swap"]

    score = state["score"]
    trace = list(state["trace"])

    nv_points, nv_reason = score_number_verification(nv)
    score += nv_points
    trace.append(_entry("number_verification", "number_verification", nv, nv_points, nv_reason, score, (nv_s, nv_e)))

    ss_points, ss_reason = score_sim_swap(ss)
    score += ss_points
    trace.append(_entry("sim_swap", "sim_swap", ss, ss_points, ss_reason, score, (ss_s, ss_e)))

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
    pn, sc = state["phone_number"], state["scenario"]
    dfp, loc = state["device_fingerprint"], state["claimed_location"]
    out = _run_parallel(state["t0"], [
        ("device_status", lambda: _device_status_client.check(pn, dfp, scenario=sc)),
        ("location_verification", lambda: _location_verification_client.verify(pn, loc, scenario=sc)),
    ])
    (ds, ds_s, ds_e), (lv, lv_s, lv_e) = out["device_status"], out["location_verification"]

    score = state["score"]
    trace = list(state["trace"])

    ds_points, ds_reason = score_device_status(ds)
    score += ds_points
    trace.append(_entry("device_status", "device_status", ds, ds_points, ds_reason, score, (ds_s, ds_e)))

    # Location is scored with the device's roaming state in hand: a mismatch
    # on a roaming device is usually travel, not spoofing (see scoring.py).
    lv_points, lv_reason = score_location_verification(lv, roaming=ds["roaming"])
    score += lv_points
    trace.append(_entry("location_verification", "location_verification", lv, lv_points, lv_reason, score, (lv_s, lv_e)))

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

    # Per-call timings, so a reviewer can see the independent CAMARA calls
    # overlapped (real parallel API activity, not a serial fake).
    timed_calls = [
        {
            "api": s["api"],
            "source": (s.get("signal") or {}).get("source"),
            "start_ms": s["timing"]["start_ms"],
            "end_ms": s["timing"]["end_ms"],
            "ms": s["timing"]["end_ms"] - s["timing"]["start_ms"],
        }
        for s in state["trace"]
        if s.get("timing")
    ]
    parallel_groups = [
        [c["api"] for c in timed_calls if c["api"] in ("number_verification", "sim_swap")],
        [c["api"] for c in timed_calls if c["api"] in ("device_status", "location_verification")],
    ]
    timing = {
        "total_ms": round((time.perf_counter() - state["t0"]) * 1000),
        "calls": timed_calls,
        "parallel_groups": [g for g in parallel_groups if len(g) > 1],
    }

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
        "timing": timing,
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
            "t0": time.perf_counter(),
            "score": 0,
            "trace": [],
            "escalate": False,
            "ai": None,
            "ai_ran": False,
            "result": None,
        }
        final_state = _compiled_graph.invoke(initial_state)
        return final_state["result"]
