"""
The three scripted demo scenarios from the pitch deck's Prototype Plan:
clean login / SIM-swap block / mismatched-onboarding step-up.

Each scenario is a complete, realistic request payload. The mock CAMARA
clients (backend/camara_apis/*) key off `scenario` to return the matching
canned signals — same orchestrator code path, three different outcomes.
This is also the "cached demo data" the Resource & Tooling Guide
recommends, so the demo never depends on a live network call.
"""

SCENARIOS = {
    "clean": {
        "id": "clean",
        "title": "Clean login",
        "description": "A returning remitter logs in from their usual phone, on their usual device. Nothing suspicious — should sail through with zero friction.",
        "request": {
            "phone_number": "+971501234567",
            "action_type": "login",
            "device_fingerprint": "device-fp-known-abc123",
            "claimed_location": "Dubai, UAE",
        },
        "expected_decision": "ALLOW",
    },
    "sim_swap_block": {
        "id": "sim_swap_block",
        "title": "SIM-swap takeover attempt",
        "description": "Same account, but the SIM was swapped 40 minutes ago and the login comes from an unrecognized device. Classic OTP-interception setup — should block.",
        "request": {
            "phone_number": "+971501234567",
            "action_type": "login",
            "device_fingerprint": "device-fp-unknown-xyz999",
            "claimed_location": "Dubai, UAE",
        },
        "expected_decision": "BLOCK",
    },
    "mismatch_stepup": {
        "id": "mismatch_stepup",
        "title": "Mismatched onboarding",
        "description": "A brand-new account onboarding from an unrecognized, roaming device whose claimed location doesn't match the network location — suspicious enough to verify further, not clear-cut enough to outright block.",
        "request": {
            "phone_number": "+971509876543",
            "action_type": "onboarding",
            "device_fingerprint": "device-fp-unknown-new777",
            "claimed_location": "Cairo, Egypt",
        },
        "expected_decision": "STEP_UP",
    },
}


def list_scenarios() -> list[dict]:
    return [
        {"id": s["id"], "title": s["title"], "description": s["description"], "expected_decision": s["expected_decision"]}
        for s in SCENARIOS.values()
    ]


def get_scenario(scenario_id: str) -> dict:
    if scenario_id not in SCENARIOS:
        raise KeyError(f"Unknown scenario '{scenario_id}'")
    return SCENARIOS[scenario_id]
