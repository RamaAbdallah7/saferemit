"""Unit tests for the risk-scoring table — the rules judges will read."""
from backend.agent.scoring import (
    decision_for_score,
    score_device_status,
    score_location_verification,
    score_number_verification,
    score_sim_swap,
)


def test_recent_sim_swap_is_high_risk():
    points, reason = score_sim_swap({"swapped": True})
    assert points == 45
    assert "SIM" in reason


def test_no_sim_swap_adds_nothing():
    assert score_sim_swap({"swapped": False}) == (0, "No recent SIM swap on this number.")


def test_unverified_number_adds_risk():
    points, _ = score_number_verification({"verified": False})
    assert points == 35


def test_verified_number_adds_nothing():
    assert score_number_verification({"verified": True})[0] == 0


def test_device_status_stacks_unknown_and_roaming():
    points, reason = score_device_status({"known_device": False, "roaming": True})
    assert points == 30
    assert "not seen" in reason and "roaming" in reason


def test_known_non_roaming_device_is_clean():
    assert score_device_status({"known_device": True, "roaming": False})[0] == 0


def test_location_mismatch_scores_more_than_partial():
    false_pts, _ = score_location_verification({"verification_result": "FALSE", "match_rate": 12})
    partial_pts, _ = score_location_verification({"verification_result": "PARTIAL", "match_rate": 54})
    true_pts, _ = score_location_verification({"verification_result": "TRUE", "match_rate": 97})
    assert false_pts > partial_pts > true_pts == 0


def test_decision_thresholds():
    assert decision_for_score(0) == "ALLOW"
    assert decision_for_score(29) == "ALLOW"
    assert decision_for_score(30) == "STEP_UP"
    assert decision_for_score(69) == "STEP_UP"
    assert decision_for_score(70) == "BLOCK"
    assert decision_for_score(100) == "BLOCK"
