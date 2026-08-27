"""
Behavioural tests for the LangGraph agent — these lock in the three
scripted demo outcomes and the "agent decides which API to call"
escalation logic that makes this agentic rather than a fixed checklist.
"""
import pytest

from backend.agent.orchestrator import SafeRemitAgent
from backend.scenarios import SCENARIOS

agent = SafeRemitAgent()


@pytest.mark.parametrize("scenario_id", list(SCENARIOS))
def test_scenario_reaches_expected_decision(scenario_id):
    preset = SCENARIOS[scenario_id]
    result = agent.decide(preset["request"], scenario=scenario_id)
    assert result["decision"] == preset["expected_decision"]


def test_clean_login_takes_the_fast_path():
    """A routine login with clean early signals must NOT call device
    status or location — that efficiency call is the agentic behaviour."""
    result = agent.decide(SCENARIOS["clean"]["request"], scenario="clean")
    assert result["apis_called"] == ["number_verification", "sim_swap"]


def test_sim_swap_attempt_escalates_to_all_four_apis():
    result = agent.decide(SCENARIOS["sim_swap_block"]["request"], scenario="sim_swap_block")
    assert result["apis_called"] == [
        "number_verification", "sim_swap", "device_status", "location_verification",
    ]


def test_onboarding_escalates_even_before_a_bad_signal():
    """Onboarding is a sensitive action, so the agent proactively pulls
    every signal regardless of how the early checks look."""
    result = agent.decide(SCENARIOS["mismatch_stepup"]["request"], scenario="mismatch_stepup")
    assert "device_status" in result["apis_called"]
    assert "location_verification" in result["apis_called"]


def test_trace_is_ordered_and_scores_are_monotonic():
    result = agent.decide(SCENARIOS["sim_swap_block"]["request"], scenario="sim_swap_block")
    running = [step["running_score"] for step in result["trace"]]
    assert running == sorted(running)
    assert result["risk_score"] == running[-1]


def test_mock_mode_is_reported():
    result = agent.decide(SCENARIOS["clean"]["request"], scenario="clean")
    assert result["camara_mode"] == "mock"
    assert result["signal_sources"] == ["mock"]
