# SafeRemit — AI-Orchestrated Anti-Fraud Layer for Cross-Border Remittances

MENA Ignite Hackathon 2026 — Theme 4: Secure Fintech, Payments & Anti-Fraud Innovation
Team: FikraX

SafeRemit is an AI agent that fuses SIM Swap, Number Verification, Device Status, and Location signals from CAMARA APIs (via Nokia Network-as-Code) into a single real-time fraud decision — stopping remittance account takeover and mule onboarding before the money moves, with zero added friction for legitimate users.

## Quickstart

**While actively developing the UI** (two terminals, live reload):

```bash
# terminal 1 — backend
cd saferemit
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload

# terminal 2 — frontend (React + Framer Motion, hot reload)
cd saferemit/frontend
npm install
npm run dev
```

Open **http://127.0.0.1:5173** — Vite proxies `/api/*` calls straight through to the backend on :8000 (see `frontend/vite.config.js`), so both sides update live as you edit.

**For a single-command demo run** (e.g. recording the submission video):

```bash
cd saferemit/frontend && npm install && npm run build
cd .. && pip install -r backend/requirements.txt
uvicorn backend.app:app
```

Open **http://127.0.0.1:8000** — the backend serves the built React app directly, so this one command is the whole prototype. (`frontend-vanilla/` is the original plain HTML/JS version, kept as a zero-dependency fallback if `frontend/dist` hasn't been built yet.)

### Configuration

Everything is optional — with nothing set, SafeRemit runs on mock CAMARA data + a deterministic rationale. `cp .env.example .env` and fill in what you have:

| Var | Effect |
|---|---|
| `NAC_API_KEY` | Switches the CAMARA clients from mock to **live** Nokia Network-as-Code calls (with automatic mock fallback on error). SIM Swap, Device Status and Location Verification run live; Number Verification needs OAuth and falls back. See `PROTOTYPE_NOTES.md`. |
| `GEMINI_API_KEY` | Turns on Gemini-generated rationale text (falls back to the deterministic template). |

`GET /api/health` reports whether you're running `live` or `mock`. Run the tests with `python -m pytest`.

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
    _nac.py           shared live Network-as-Code HTTP helper + graceful fallback
  config.py           all env-driven config (NAC_API_KEY, GEMINI_API_KEY, ...)
  scenarios.py         the 3 demo scenarios (clean / sim-swap block / mismatch step-up)
  tests/               pytest suite — scoring rules, agent behaviour, API surface
  app.py               FastAPI app — /api/decide, /api/scenarios, /api/health, serves the frontend
frontend/                React + Vite + Framer Motion demo UI (scenario picker,
                          animated reasoning trace, live decision badge)
  src/components/        ScenarioTabs, AppMock, ReasoningPanel, DecisionBadge, TraceList
  src/api.js              talks to the backend; PREVIEW_REQUESTS mirrors scenarios.py
frontend-vanilla/        original plain HTML/JS/CSS version — zero build step,
                          kept as a fallback (see backend/app.py)
demo/
  DEMO_SCRIPT.md        script for the 3-minute submission video
docs/
  pitch-deck.html      single-file pitch (problem, agent, live status, business)
PROTOTYPE_NOTES.md      what's live vs. mocked, how to go live, compliance checklist
```

## Tech stack (and why, per the AI Resource & Tooling Guide)

This is the Guide's recommended **"Intermediate stack (Python)"** — LangGraph agent + Gemini + CAMARA APIs as agent tools.

- **LangGraph** — §2, "Code-first agent frameworks." Chosen because the agent's actual behavior (conditional escalation — call the cheap checks first, only pull device/location data when the action is sensitive or an early signal looks wrong) is naturally a small directed graph, not a linear pipeline. This is what makes it *agentic* per the Guide: "each CAMARA API [is] a tool the agent decides when to call, not a button the user presses."
- **CAMARA APIs on Nokia Network-as-Code** — SIM Swap, Device Status (roaming + connectivity) and Location Verification run as **live calls** against the NaC apihub gateway in Simulator mode; Number Verification is wired but needs the OAuth leg. Every call degrades to cached mock data on failure.
- **Google AI Studio / Gemini** (`gemini-2.5-flash`) — §3, "Hosted APIs with a free tier." Rewrites the deterministic rationale into a tighter analyst-facing sentence. Optional — the deterministic template is the demo-day safety net.
- **FastAPI + React/Vite** — kept simple so any judge can clone and run it in under a minute with one command. Live CAMARA calls degrade gracefully to cached mock data (Guide's tip: "a recorded fallback keeps the demo running").

## Pitch

`docs/pitch-deck.html` — a single-file, self-contained pitch (problem, the agent, live CAMARA status, business model). Open it in a browser, or publish it as a shareable page.

## Submission checklist

- [x] Idea Capture Template — submitted, shortlisted
- [ ] Prototype working end-to-end with live Nokia NaC calls (currently mocked, see `PROTOTYPE_NOTES.md`)
- [ ] Pitch Deck update (architecture + business model sections)
- [ ] 3-minute demo video (script ready in `demo/DEMO_SCRIPT.md`)
- [ ] GitHub repo link in final submission
