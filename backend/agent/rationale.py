"""
Builds the plain-language rationale shown with the decision.

Three cases:
  * rules only (no Gemini key, or the LLM call failed) — a deterministic
    sentence assembled from the scored signals. This always works, so the
    demo never depends on an external call.
  * rules and AI analyst agree — lead with the AI's reasoning, note the
    agreement as added confidence.
  * they disagree — state both calls, that the stricter one was taken,
    and flag it for human review.
"""


def _driving_reasons(trace: list[dict]) -> str:
    return "; ".join(step["reason"] for step in trace if step.get("points", 0) > 0)


def _rules_sentence(decision: str, score: int, trace: list[dict]) -> str:
    score = min(100, score)
    reasons = _driving_reasons(trace)
    if decision == "ALLOW":
        return (
            "All signals check out — verified number, no recent SIM swap, known device, "
            "matching location. Allowed with no friction."
            if not reasons
            else "Minor signals noted but well below the risk threshold — allowed with no added friction."
        )
    if decision == "BLOCK":
        return f"Blocked (risk score {score}/100): {reasons}"
    return f"Step-up verification required (risk score {score}/100): {reasons}"


def _label(decision: str) -> str:
    return decision.replace("_", "-")


def explain(decision, score, trace, *, ai=None, agreement=None, rules_decision=None) -> dict:
    """Returns {"text": str, "source": "rules" | "gemini" | "reconciled"}."""
    if not ai:
        return {"text": _rules_sentence(decision, score, trace), "source": "rules"}

    ai_reason = ai.get("reasoning") or "signal combination assessed."
    if agreement:
        return {
            "text": f"{ai_reason} The rules score agrees — confidence in the {_label(decision)} call is high.",
            "source": "gemini",
        }
    return {
        "text": (
            f"Split call: the rules score points to {_label(rules_decision or decision)}, "
            f"the AI analyst to {_label(ai['decision'])} — {ai_reason} "
            f"Taking the stricter decision ({_label(decision)}) and flagging for human review."
        ),
        "source": "reconciled",
    }
