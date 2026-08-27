"""
The LLM analyst step.

The deterministic scoring table (scoring.py) is fast, transparent and
always runs. This module adds a second opinion: it hands Gemini the same
CAMARA signals a human fraud analyst would see and asks it to reason
about the *combination* — patterns a fixed points table misses (e.g. "a
SIM swap alone is noise, but a SIM swap plus a brand-new device plus a
transfer is a textbook takeover").

`assess()` returns a structured verdict, or None if no key is configured
or the call fails. The orchestrator then reconciles the two opinions in
finalize() — taking the stricter decision and flagging any disagreement.
This keeps the demo safe (rules-only still works) while making the AI a
real part of the decision, not just a rewording of it.

Gemini / Google AI Studio is on the hackathon's AI Resource & Tooling
Guide, section 3.
"""
import json
import re

import requests

from .. import config

_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

_SYSTEM = """You are a fraud-decision analyst for a cross-border remittance service in the MENA region.
You receive real-time telecom network signals (from CAMARA APIs) about the device making a request.
Two fraud patterns dominate this corridor:
  - SIM-swap account takeover: a recent SIM swap lets a fraudster intercept the OTP.
  - Synthetic-identity mule onboarding: accounts opened remotely on unrecognized, often roaming devices.

Weigh the SIGNALS AS A COMBINATION, not individually. A single weak signal is usually noise;
several weak signals that fit one of the patterns above is high confidence.

Respond with ONLY a JSON object, no prose:
{"decision": "ALLOW" | "STEP_UP" | "BLOCK",
 "risk_score": <integer 0-100>,
 "reasoning": "<= 40 words, the specific signal combination that drove the call>"}
ALLOW = proceed with no friction. STEP_UP = require extra verification. BLOCK = stop the transaction."""


def available() -> bool:
    return config.USE_LLM_ASSESSMENT


def _signal_lines(trace: list[dict]) -> str:
    lines = []
    for step in trace:
        sig = step.get("signal")
        if not sig:
            continue
        if step["step"] == "number_verification":
            lines.append(f"- Number verification: {'verified' if sig['verified'] else 'NOT verified'} (source: {sig['source']})")
        elif step["step"] == "sim_swap":
            lines.append(f"- SIM swap in the risk window: {'YES' if sig['swapped'] else 'no'} (source: {sig['source']})")
        elif step["step"] == "device_status":
            lines.append(
                f"- Device: {'known to this account' if sig['known_device'] else 'NOT seen on this account before'}, "
                f"{'roaming' if sig['roaming'] else 'on home network'} (source: {sig['source']})"
            )
        elif step["step"] == "location_verification":
            lines.append(
                f"- Claimed location vs network location: {sig['verification_result']} "
                f"(match rate {sig['match_rate']}%) (source: {sig['source']})"
            )
    return "\n".join(lines)


def assess(action_type: str, trace: list[dict]) -> dict | None:
    """Ask Gemini for a second-opinion verdict. Returns
    {"decision", "risk_score", "reasoning"} or None on any failure."""
    if not available():
        return None

    prompt = (
        f"{_SYSTEM}\n\n"
        f"Action being attempted: {action_type}\n"
        f"Signals gathered:\n{_signal_lines(trace)}\n\n"
        "Your JSON verdict:"
    )
    try:
        resp = requests.post(
            _ENDPOINT.format(model=config.GEMINI_MODEL),
            params={"key": config.GEMINI_API_KEY},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json",
                    # A fraud verdict needs very little deliberation; a small
                    # thinking budget keeps the call near 2s instead of ~6s.
                    "thinkingConfig": {"thinkingBudget": 128},
                },
            },
            timeout=config.GEMINI_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        data = _parse(text)
        if data is None:
            return None
        decision = str(data.get("decision", "")).upper()
        if decision not in {"ALLOW", "STEP_UP", "BLOCK"}:
            return None
        return {
            "decision": decision,
            "risk_score": max(0, min(100, int(data.get("risk_score", 0)))),
            "reasoning": str(data.get("reasoning", "")).strip(),
        }
    except Exception:
        return None


def _parse(text: str) -> dict | None:
    text = text.strip()
    try:
        return json.loads(text)
    except ValueError:
        pass
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except ValueError:
            return None
    return None
