"""
The three scripted demo scenarios from the pitch deck's Prototype Plan:
clean login / SIM-swap block / mismatched-onboarding step-up.

Each scenario is a complete, realistic request payload. In mock mode the
CAMARA clients key off `scenario` to return matching canned signals.

`live_phone`, where present, is a Nokia NaC **simulator MSISDN** whose
network profile naturally produces this scenario's outcome — so when the
backend runs in live mode (`NAC_API_KEY` set) these scenarios execute as
real CAMARA calls and still land on the expected decision. The simulator
map (from the NaC docs):

    +99999991001  not swapped, not roaming, location TRUE   -> ALLOW
    +99999991000  swapped, roaming, location FALSE          -> BLOCK
    +99999991002  swapped, roaming, location PARTIAL
    +99999990500  HTTP 500 on every call  -> exercises mock fallback

The mismatched-onboarding step-up case has no single simulator number
that lands between the thresholds, so it stays on mock data even in live
mode (this is the "cached demo data" fallback the Tooling Guide
recommends). The Custom request tab is there for free-form live calls.
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
        "live_phone": "+99999991001",
    },
    "sim_swap_block": {
        "id": "sim_swap_block",
        "title": "SIM-swap takeover attempt",
        "description": "Same account, but the SIM was swapped minutes ago and the login comes from an unrecognized device. Classic OTP-interception setup — should block.",
        "request": {
            "phone_number": "+971501234567",
            "action_type": "login",
            "device_fingerprint": "device-fp-unknown-xyz999",
            "claimed_location": "Dubai, UAE",
        },
        "expected_decision": "BLOCK",
        "live_phone": "+99999991000",
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
        "live_phone": None,
    },
}


def list_scenarios() -> list[dict]:
    return [
        {
            "id": s["id"],
            "title": s["title"],
            "description": s["description"],
            "expected_decision": s["expected_decision"],
            "live_capable": s["live_phone"] is not None,
            "live_phone": s["live_phone"],
            "request": s["request"],
        }
        for s in SCENARIOS.values()
    ]


def get_scenario(scenario_id: str) -> dict:
    if scenario_id not in SCENARIOS:
        raise KeyError(f"Unknown scenario '{scenario_id}'")
    return SCENARIOS[scenario_id]
