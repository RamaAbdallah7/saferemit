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

Two things are served from the same process:

- **http://127.0.0.1:8000** — an interactive walkthrough of the whole system
  (`frontend/dist/index.html`, no backend calls — a presentation layer).
- **http://127.0.0.1:8000/app** — the actual working prototype (React UI,
  real `/api/decide` calls). This is what the rest of this README describes.

Live deploy: **saferemit.onrender.com** (walkthrough) /
**saferemit.onrender.com/app** (prototype).

For UI development, run `npm run dev` in `frontend/` (Vite on :5173, proxies
`/api` to the backend on :8000) alongside `uvicorn backend.app:app --reload`.
Vite's `base` is `/app/`, so a dev build only ever touches `frontend/dist/app/`
— the walkthrough at `frontend/dist/index.html` is a separately committed file.

### Configuration

Copy `.env.example` to `.env`. Everything is optional — with nothing set, the app
runs on mock CAMARA data and a rules-only decision.

| Var | Effect |
|---|---|
| `NAC_API_KEY` | Switches the CAMARA clients to **live** calls against Nokia Network-as-Code (Simulator network). Each call falls back to cached data on failure. |
| `GEMINI_API_KEY` | Turns on the **AI analyst**: on the escalation path, Gemini reasons about the signal combination and its verdict is reconciled with the rules score. |

`GET /api/health` reports the current mode. `python -m pytest` runs the test suite
(27 tests; live/LLM paths are opt-in via `RUN_LIVE_CAMARA=1`).

Every `/api/decide` response also carries a `timing` block — each CAMARA call's
start/end offset in milliseconds, and which calls ran in the same
`parallel_groups`. It's there so "the checks run in parallel" is checkable, not
just claimed: Number Verification and SIM Swap start within ~1ms of each other,
same for Device Status and Location Verification. The backend also logs every
CAMARA HTTP call (with its worker thread id) to stdout for the same reason.

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

Location is deliberately never a standalone reason to block: a full mismatch adds
+30 (STEP-UP, not BLOCK), and if the device is roaming that's read as travel and
halved to +15 — a VPN or a trip abroad doesn't get treated like spoofing. See
`backend/agent/scoring.py`.

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
  dist/index.html        the interactive walkthrough — committed directly, not built
  dist/app/              `npm run build` output (Vite base=/app/) — the prototype
  src/components/        ScenarioTabs · AppMock · ReasoningPanel · RiskGauge ·
                          TraceList · ApiTimeline (parallel-call proof) · Story
docs/
  walkthrough.html       source of the interactive walkthrough (same file as dist/index.html)
  architecture.html      sequence / component / agent-graph / LLM+scoring diagrams
  diagrams/               exported PNGs of the above, incl. a C4 container diagram
  pitch-deck.html        single-file pitch
  HOW_IT_WORKS.md        plain-English walkthrough
  compliance-audit.html  line-by-line audit against the hackathon rules
PROTOTYPE_NOTES.md       live vs. mock status, portal setup, rules-compliance checklist
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
- [x] Working prototype: live CAMARA calls, LLM analyst, 27 automated tests
- [x] Deployed — saferemit.onrender.com (walkthrough) / saferemit.onrender.com/app (prototype)
- [x] Pitch deck (submitted as `.pptx`; `docs/pitch-deck.html` is an HTML reference version)
- [x] GitHub repo link in the submission
- [x] 3-minute demo video — recorded and submitted
