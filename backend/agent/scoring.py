"""
Risk scoring rules for the SafeRemit orchestration agent.

Kept as an explicit, named table (rather than buried inline in the
orchestrator) so judges can see exactly how each CAMARA signal maps to
risk points, and so you can tune it without touching orchestration logic.
"""

# Decision thresholds on a 0-100 risk score.
ALLOW_BELOW = 30
BLOCK_AT_OR_ABOVE = 70
# Between ALLOW_BELOW and BLOCK_AT_OR_ABOVE -> STEP_UP verification.

RECENT_SIM_SWAP_WINDOW_HOURS = 72


def score_sim_swap(sim_swap_result: dict) -> tuple[int, str]:
    if sim_swap_result["swapped"]:
        return 45, "SIM was swapped within the last 72 hours — the #1 precursor to OTP-interception takeover."
    return 0, "No recent SIM swap on this number."


def score_number_verification(nv_result: dict) -> tuple[int, str]:
    if not nv_result["verified"]:
        return 35, "Carrier could not verify this number is on the device making the request."
    return 0, "Number verified as the device actually placing the request."


def score_device_status(ds_result: dict) -> tuple[int, str]:
    points = 0
    reasons = []
    if not ds_result["known_device"]:
        points += 20
        reasons.append("device fingerprint not seen on this account before")
    if ds_result["roaming"]:
        points += 10
        reasons.append("device is roaming, outside its usual network")
    reason = "; ".join(reasons) if reasons else "recognized device, not roaming."
    return points, reason


def score_location_verification(lv_result: dict) -> tuple[int, str]:
    result = lv_result["verification_result"]
    if result == "FALSE":
        return 30, f"Claimed location does not match network location (match rate {lv_result['match_rate']}%)."
    if result == "PARTIAL":
        return 15, f"Claimed location only partially matches network location (match rate {lv_result['match_rate']}%)."
    return 0, f"Claimed location matches network location (match rate {lv_result['match_rate']}%)."


def decision_for_score(score: int) -> str:
    if score < ALLOW_BELOW:
        return "ALLOW"
    if score >= BLOCK_AT_OR_ABOVE:
        return "BLOCK"
    return "STEP_UP"
