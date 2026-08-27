"""API-surface tests via FastAPI's TestClient."""
from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_health_reports_mock_mode_by_default():
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["camara_mode"] == "mock"


def test_scenarios_lists_the_three_demos():
    body = client.get("/api/scenarios").json()
    ids = {s["id"] for s in body["scenarios"]}
    assert ids == {"clean", "sim_swap_block", "mismatch_stepup"}


def test_decide_by_scenario():
    body = client.post("/api/decide", json={"scenario": "sim_swap_block"}).json()
    assert body["decision"] == "BLOCK"
    assert body["rationale"]
    assert body["trace"][0]["step"] == "number_verification"


def test_decide_unknown_scenario_is_404():
    assert client.post("/api/decide", json={"scenario": "nope"}).status_code == 404


def test_decide_freeform_request_requires_phone_number():
    assert client.post("/api/decide", json={"action_type": "login"}).status_code == 400


def test_decide_freeform_request_runs():
    body = client.post("/api/decide", json={
        "phone_number": "+971500000000",
        "action_type": "transfer",
        "device_fingerprint": "device-fp-known-abc123",
        "claimed_location": "Dubai, UAE",
    }).json()
    assert body["decision"] in {"ALLOW", "STEP_UP", "BLOCK"}
    # transfer is a sensitive action -> agent escalates to all four APIs
    assert "location_verification" in body["apis_called"]
