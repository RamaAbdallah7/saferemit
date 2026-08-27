# SafeRemit — AI-Orchestrated Anti-Fraud Layer for Cross-Border Remittances

MENA Ignite Hackathon 2026 — Theme 4: Secure Fintech, Payments & Anti-Fraud Innovation
Team: FikraX

SafeRemit is an AI agent that fuses SIM Swap, Number Verification, Device Status, and Location signals from CAMARA APIs (via Nokia Network-as-Code) into a single real-time fraud decision — stopping remittance account takeover and mule onboarding before the money moves, with zero added friction for legitimate users.

## Quickstart

```bash
cd saferemit
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload
```

Then open **http://127.0.0.1:8000** — the demo UI is served directly by the backend, so this one command is the whole prototype.

Optional: `export GEMINI_API_KEY=...` before starting the server to turn on live Gemini-generated rationale text (see `PROTOTYPE_NOTES.md`). Works fine without it — falls back to a deterministic explainer.

## How it works

```
Remittance app event (login / onboarding / transfer)
        |
        v
+-------------------------------------------------------+
|              SafeRemitAgent (LangGraph)                |
|                                                         |
|  1. Number Verification  ──always──┐                   |
|  2. SIM Swap check       ──always──┤                   |
|                                     v                   |
|                          escalate?  (sensitive action,  |
|                                      or an early signal |
|                                      already looks bad) |
|                              /            \             |
|                           no              yes           |
|                            |                |           |
|                     fast-path ALLOW   3. Device Status  |
|                                        4. Location Ver. |
|                                              |           |
|                                     fuse all signals →  |
|                                   risk score (0–100) →  |
|                              ALLOW / STEP_UP / BLOCK    |
|                                              |           |
|                                  Gemini (or template)   |
|                                   plain-language         |
|                                   rationale              |
+-------------------------------------------------------+
        |
        v
  decision + risk score + full reasoning trace → UI
```

The agent doesn't call all four CAMARA APIs on every request — it escalates the way a human fraud analyst would, which is what makes this "agentic" rather than a fixed checklist (see `backend/agent/orchestrator.py` for the full reasoning).

## Project layout

```
backend/
  camara_apis/        mock CAMARA API clients (SIM Swap, Number Verification,
                       Device Status, Location Verification) — shaped to match
                       the real Nokia Network-as-Code responses; see each
                       file's docstring for the live swap-in
  agent/
    orchestrator.py    the LangGraph agent — orchestration + escalation logic
    scoring.py         risk-scoring rules, kept explicit and separate
    rationale.py        plain-language explanation, optional live Gemini call
  scenarios.py         the 3 demo scenarios (clean / sim-swap block / mismatch step-up)
  app.py               FastAPI app — /api/decide, /api/scenarios, serves the frontend
frontend/
  index.html, style.css, app.js   the demo UI (scenario picker + live reasoning panel)
demo/
  DEMO_SCRIPT.md        script for the 3-minute submission video
PROTOTYPE_NOTES.md      what's mocked vs. real, how to go live, compliance checklist
```

## Tech stack (and why, per the AI Resource & Tooling Guide)

- **LangGraph** — orchestration framework, listed in the Guide's "Code-first agent frameworks." Chosen because the agent's actual behavior (conditional escalation) is naturally a small directed graph, not a linear pipeline.
- **Google AI Studio / Gemini** — listed in the Guide's "LLMs and Model APIs," used to rewrite the deterministic rationale into a tighter analyst-facing sentence. Optional — the deterministic template is the safety net for a live demo.
- **FastAPI + vanilla JS** — kept deliberately simple so any judge can clone this and have it running in under a minute with one command.

## Submission checklist

- [x] Idea Capture Template — submitted, shortlisted
- [ ] Prototype working end-to-end with live Nokia NaC calls (currently mocked, see `PROTOTYPE_NOTES.md`)
- [ ] Pitch Deck update (architecture + business model sections)
- [ ] 3-minute demo video (script ready in `demo/DEMO_SCRIPT.md`)
- [ ] GitHub repo link in final submission
