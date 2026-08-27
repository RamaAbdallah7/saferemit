"""
Turns the agent's signal trace into a plain-language rationale.

Default mode is fully deterministic (template-based) so the demo works
with zero API keys and zero network dependency — good for a reliable
3-minute demo video where you can't afford a flaky API call.

Optional mode: if GEMINI_API_KEY is set in the environment, `explain()`
asks Gemini to rewrite the same trace into a tighter, more natural
sentence. The deterministic summary is always computed first and passed
in as ground truth, so a failed/slow Gemini call never changes the
decision — only the wording of the explanation, with automatic fallback
to the template if the call errors or times out.

IMPORTANT: confirm Gemini is actually on the hackathon's approved AI
Resource & Tooling Guide before relying on this in your submission — see
PROTOTYPE_NOTES.md. If it isn't approved, leave GEMINI_API_KEY unset and
the deterministic explainer is your rationale generator, no code changes
needed.
"""
import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_TIMEOUT_SECONDS = 4


def _template_rationale(decision: str, score: int, trace: list[dict]) -> str:
    driving = [step for step in trace if step["points"] > 0]
    if decision == "ALLOW":
        if not driving:
            return "All signals check out — verified number, no recent SIM swap, known device, matching location. Allowed with no friction."
        return "Minor signals noted but well below the risk threshold — allowed with no added friction."

    reasons = "; ".join(step["reason"] for step in driving)
    if decision == "BLOCK":
        return f"Blocked (risk score {score}/100): {reasons}"
    return f"Step-up verification required (risk score {score}/100): {reasons}"


def explain(decision: str, score: int, trace: list[dict]) -> dict:
    """Returns {"text": str, "source": "template" | "gemini"}."""
    template_text = _template_rationale(decision, score, trace)

    if not GEMINI_API_KEY:
        return {"text": template_text, "source": "template"}

    try:
        prompt = (
            "Rewrite this fraud-decision rationale in one tight, plain-language "
            "sentence for a bank fraud analyst. Keep every fact, change nothing "
            f"about the decision itself.\n\nDecision: {decision}\n"
            f"Risk score: {score}/100\nSignals: {template_text}"
        )
        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
            params={"key": GEMINI_API_KEY},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=GEMINI_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        return {"text": text, "source": "gemini"}
    except Exception:
        # Never let a flaky LLM call break the decision — fall back silently.
        return {"text": template_text, "source": "template"}
