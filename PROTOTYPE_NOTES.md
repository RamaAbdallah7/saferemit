# Prototype notes — read this before the Live Demo round

## What's real vs. mocked right now

- **Real:** the FastAPI backend, the LangGraph orchestration agent, the risk-scoring logic, the escalation/branching decision, the rationale generator (with optional live Gemini call), the full frontend UI, and the `pytest` suite (`python -m pytest`).
- **Live-or-mock:** the four CAMARA API clients (`backend/camara_apis/*.py`). Each one calls the real Nokia Network-as-Code endpoint **when `NAC_API_KEY` is set**, and otherwise returns realistic scenario-keyed canned data. If a live call errors or times out it falls back to the mock automatically and marks the signal `source: "mock-fallback"`.

This graceful degradation is exactly what the Resource & Tooling Guide tells you to build: *"Have a clear fallback when an API or model is rate-limited"* and *"Cache demo data. Live API calls fail at the worst moment."* `GET /api/health` reports whether you're currently `live` or `mock`, and every decision result carries `camara_mode` + `signal_sources`.

## To go live with Nokia Network-as-Code

1. Register at https://networkascode.nokia.io/ (each teammate individually — no org setup needed).
2. In the **API Hub**, subscribe to: SIM Swap, Number Verification, Device Status, Location Verification.
3. Copy your **`x-rapidapi-key`** (shown on your app / any API's "Endpoints" tab).
4. `cp .env.example .env` and paste the key into `NAC_API_KEY=`. That's the whole switch — restart the backend and `/api/health` should show `"camara_mode": "live"`.
5. Test against the portal's **simulator numbers** (in the NaC docs), not real SIMs.
6. **Verify the request/response mapping** in each `backend/camara_apis/*.py` `_live()` method against your portal's actual "Endpoints" tab — the CAMARA path prefixes and field names there are the source of truth; adjust `_live()` and, if a field name differs, `backend/agent/scoring.py`. The mock clients stay in place as the demo-day safety net — don't delete them.

## Where to tune the Framer Motion animation

The frontend was rebuilt on React + Vite specifically so this part is easy to iterate on with live reload (`npm run dev` in `frontend/`). Entry points:

- `frontend/src/components/TraceList.jsx` — `listVariants`/`itemVariants` control the staggered reveal of each reasoning step. `staggerChildren` (currently 0.14s) is the gap between steps appearing.
- `frontend/src/components/ReasoningPanel.jsx` — `RATIONALE_DELAY_S` times the rationale fade-in to land after the last trace item. If you change `staggerChildren` or the trace length assumption, update this too (it's a plain formula, not auto-derived, on purpose — easy to see and change).
- `frontend/src/components/DecisionBadge.jsx` — the spring transition on the badge itself, plus `useCountUp` for the risk-score number animation.
- `frontend/src/components/ScenarioTabs.jsx` — the sliding active-tab pill, done with a shared `layoutId` (Framer Motion animates the transform between tabs automatically).
- `frontend/src/styles.css` — colors/spacing/layout; unrelated to Framer Motion but often edited alongside it.

## To turn on the live Gemini rationale

1. Get a free key at https://aistudio.google.com/ (Google AI Studio — listed in the Resource & Tooling Guide, section 3).
2. `export GEMINI_API_KEY=your-key-here` before starting the backend.
3. That's it — `backend/agent/rationale.py` picks it up automatically and falls back to the deterministic template if the call fails or times out, so this is safe to leave on during a live demo.

## Compliance checklist against the hackathon rules

- [x] Uses **≥1 CAMARA API on Nokia Network-as-Code** — four: SIM Swap, Number Verification, Device Status, Location Verification. Live-or-mock; live path is one env var away.
- [x] **AI agent layer** orchestrates those APIs as trusted real-time signals, not user-triggered buttons — `backend/agent/orchestrator.py`, the conditional escalation edge is the agentic part. Matches the Guide's tip: *"Treat each CAMARA API as a tool the agent decides when to call."*
- [x] **Agent built only with Resource & Tooling Guide tools** — verified against the guide PDF: **LangGraph** (§2, "Code-first agent frameworks") + **Google AI Studio / Gemini** (§3, "Hosted APIs with a free tier"). No external tooling in the agent layer.
- [x] Architecture matches the Guide's recommended **"Intermediate stack (Python)"**: LangGraph agent + Gemini + CAMARA APIs as agent tools.
- [x] Follows the Guide's demo tips: graceful degradation, cached demo data, reasoning trace shown on screen.
- [x] **Original code**, written for this hackathon (repo history starts 2026-08-27, inside the Jul 1 – Sep 13 window).
- [x] Aligned to **Theme 4** — Secure Fintech, Payments & Anti-Fraud Innovation.
- [x] Team size 2 (≤ 5).
- [ ] **Still to do:** get the Nokia NaC key + test the 4 live calls against simulator numbers; update the pitch deck (architecture + business model); record the 3-minute demo video; put the GitHub link in the final submission.
- [ ] **Check yourselves:** both team members are 18+ and resident in an Arab League country or Türkiye.

## Suggested day-by-day for the ~17 days you have

1. **Day 1–2:** Register on Nokia NaC, get Gemini key, get this prototype running locally, read the NaC API docs for the 4 endpoints you need.
2. **Day 3–6:** Swap the 4 mock clients for real sandbox calls, one at a time, testing each against the existing 3 scenarios so you know immediately if a real response breaks the scoring logic.
3. **Day 7–9:** Polish the frontend — this is what's on screen for your 3-minute video, so it's worth the extra time.
4. **Day 10–11:** Record the demo video (3 scripted scenarios — see `demo/DEMO_SCRIPT.md`), write the final pitch deck sections (business model, architecture diagram).
5. **Day 12–13:** Buffer for the inevitable — sandbox rate limits, a teammate's laptop issue, etc.
6. **By Sep 13:** Final submission — Idea Capture Template (if it needs updating), Pitch Deck, GitHub repo link, demo video.
