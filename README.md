# SafeRemit — AI-Orchestrated Anti-Fraud Layer for Cross-Border Remittances

**GSMA MENA Ignite Hackathon 2026 · Theme 4: Secure Fintech, Payments & Anti-Fraud Innovation · Team FikraX**

SafeRemit is an AI agent that sits between a remittance app and its transaction
pipeline. On every login, onboarding or transfer it pulls the telecom-network
signals a fraudster can't fake — recent SIM swap, device roaming, whether the
network has seen this handset before, whether the device is really where it
claims — and turns them into one real-time decision: **ALLOW**, **STEP-UP**
verification, or **BLOCK**, with a plain-language reason.

It targets the two fraud patterns that dominate the MENA remittance corridor:
SIM-swap account takeover, and synthetic-identity mule onboarding. Static OTP and
document KYC catch neither in real time.

## Quickstart

```bash
# one-time
cd frontend && npm install && npm run build && cd ..
pip install -r backend/requirements.txt

# run the whole prototype
python -m uvicorn backend.app:app
```

Open **http://127.0.0.1:8000**.

For UI development, run `npm run dev` in `frontend/` (Vite on :5173, proxies
`/api` to the backend on :8000) alongside `uvicorn backend.app:app --reload`.

### Configuration

Copy `.env.example` to `.env`. Everything is optional — with nothing set, the app
runs on mock CAMARA data and a rules-only decision.

| Var | Effect |
|---|---|
| `NAC_API_KEY` | Switches the CAMARA clients to **live** calls against Nokia Network-as-Code (Simulator network). Each call falls back to cached data on failure. |
| `GEMINI_API_KEY` | Turns on the **AI analyst**: on the escalation path, Gemini reasons about the signal combination and its verdict is reconciled with the rules score. |

`GET /api/health` reports the current mode. `python -m pytest` runs the test suite
(25 tests; live/LLM paths are opt-in via `RUN_LIVE_CAMARA=1`).

## How it works

```
  Remittance event (login / onboarding / transfer)
        │
        ▼
  ┌── initial checks ──────────────┐   Number Verification + SIM Swap, in parallel.
  │                                │   Clean result on a routine login → stop here.
  └───────────────┬────────────────┘
        escalate? │  (sensitive action, or an early signal already looks wrong)
         ┌────────┴────────┐
        no                yes
         │                 │
         │        ┌── escalated checks ──┐   Device Status + Location Verification,
         │        │                      │   in parallel.
         │        └──────────┬───────────┘
         │                   ▼
         │        ┌── AI analyst (Gemini) ┐   Reasons about the signal *combination*
         │        │                       │   like a fraud analyst → its own verdict.
         │        └──────────┬────────────┘
         └───────────────────┤
                             ▼
                    ┌── finalize ──────────┐   Reconcile: rules score + AI verdict.
                    │                      │   Take the stricter decision; flag any
                    └──────────────────────┘   disagreement for human review.
                             │
                             ▼
        decision + risk 0–100 + full reasoning trace → UI
```

The agent doesn't call every CAMARA API on every request — it escalates the way a
human fraud analyst would. That conditional branch, plus the LLM reasoning step,
is what makes it *agentic* rather than a fixed checklist. Every path degrades to
rules-only if Gemini is unset or slow, and to cached data if a CAMARA call fails —
so a demo never stalls.

## Project layout

```
backend/
  camara_apis/          live-or-mock CAMARA clients (SIM Swap, Number Verification,
    _nac.py             Device Status, Location Verification) + the shared HTTP helper
  agent/
    orchestrator.py     the LangGraph agent — parallel checks, conditional escalation
    scoring.py          the transparent 0-100 risk-scoring rules
    assessment.py       the Gemini analyst — reasons about the signal combination
    rationale.py        assembles the plain-language rationale (3-way: rules / agree / split)
  config.py             all env-driven config
  scenarios.py          the 3 scripted demo scenarios
  tests/                pytest — scoring, agent behaviour, reconciliation, API surface
  app.py                FastAPI — /api/decide, /api/scenarios, /api/health, serves the UI
frontend/               React + Vite + Framer Motion
  src/components/        ScenarioTabs · AppMock · ReasoningPanel · DecisionBadge · TraceList
demo/DEMO_SCRIPT.md     3-minute submission-video script
docs/
  pitch-deck.html       single-file pitch
  HOW_IT_WORKS.md       plain-English walkthrough
PROTOTYPE_NOTES.md      live vs. mock status, portal setup, rules-compliance checklist
```

## Tech stack (per the AI Resource & Tooling Guide)

This is the Guide's recommended **"Intermediate stack (Python)"** — a LangGraph
agent, Gemini, and CAMARA APIs as the agent's data tools.

- **LangGraph** (§2, code-first agent frameworks) — the agent is a directed graph
  with a conditional escalation edge and an LLM reasoning node, not a linear
  pipeline.
- **Google AI Studio / Gemini** `gemini-3.6-flash` (§3, hosted APIs with a free
  tier) — the analyst step. Reconciled with, not replacing, the deterministic
  score.
- **CAMARA APIs on Nokia Network-as-Code** — SIM Swap, Device Status and Location
  Verification run as live calls in Simulator mode; Number Verification is wired
  (it's CAMARA 3-legged OAuth — device-side consent — so it degrades to mock).
- **FastAPI + React/Vite** — one command to run the whole thing.

## Submission checklist

- [x] Idea Capture Template — shortlisted
- [x] Working prototype: live CAMARA calls, LLM analyst, 25 automated tests
- [x] Pitch deck — `docs/pitch-deck.html`
- [ ] 3-minute demo video — script in `demo/DEMO_SCRIPT.md`
- [ ] GitHub repo link in the final submission
