# Prototype notes — read this before the Live Demo round

## What's real vs. mocked right now

- **Real:** the FastAPI backend, the LangGraph orchestration agent, the risk-scoring logic, the escalation/branching decision, the rationale generator (with optional live Gemini call), and the full frontend UI.
- **Mocked:** the four CAMARA API responses (`backend/camara_apis/*.py`). Each mock returns realistic, scenario-keyed canned data shaped like the real Nokia Network-as-Code response, with a `TODO (swap-in)` comment showing exactly what real call replaces it.

This split is deliberate and matches the Resource & Tooling Guide's own advice: *"Cache demo data. Live API calls fail at the worst moment; a recorded fallback keeps the demo running."* Keep the mocks working as your safety net even after you wire up live calls.

## To swap in live Nokia Network-as-Code calls

1. Register at https://networkascode.nokia.io/ (each teammate can register individually — no org setup needed).
2. Get your API key/token from the developer portal.
3. In each `backend/camara_apis/*.py` file, replace the body of the client method with the real SDK/HTTP call shown in that file's docstring. Keep the same return shape (or update `backend/agent/scoring.py` to match) so the orchestrator doesn't need to change.
4. Use the portal's simulator numbers for testing rather than real SIMs — this is what the platform is built for.
5. Keep the mock clients in the codebase (don't delete them) — fall back to them if the live sandbox is rate-limited or flaky during your actual demo.

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

- [x] Uses CAMARA APIs on the Nokia NaC platform (SIM Swap, Number Verification, Device Status, Location Verification) — mocked now, swap-in path documented above.
- [x] AI agent layer intelligently orchestrates those APIs as real-time signals, not user-triggered buttons (see `backend/agent/orchestrator.py` — the escalation branch is the "agentic" part).
- [x] Agent layer built using a tool from the Resource & Tooling Guide: **LangGraph** (section 2) for orchestration, **Google AI Studio / Gemini** (section 3) for the optional reasoning rewrite.
- [x] Original code, written for this hackathon.
- [x] Aligned to Theme 4 — Secure Fintech, Payments & Anti-Fraud Innovation.
- [ ] **You still need to:** confirm your Nokia NaC sandbox access works end-to-end before the demo, record the 3-minute video, and push this repo to GitHub (both required submission deliverables).

## Suggested day-by-day for the ~17 days you have

1. **Day 1–2:** Register on Nokia NaC, get Gemini key, get this prototype running locally, read the NaC API docs for the 4 endpoints you need.
2. **Day 3–6:** Swap the 4 mock clients for real sandbox calls, one at a time, testing each against the existing 3 scenarios so you know immediately if a real response breaks the scoring logic.
3. **Day 7–9:** Polish the frontend — this is what's on screen for your 3-minute video, so it's worth the extra time.
4. **Day 10–11:** Record the demo video (3 scripted scenarios — see `demo/DEMO_SCRIPT.md`), write the final pitch deck sections (business model, architecture diagram).
5. **Day 12–13:** Buffer for the inevitable — sandbox rate limits, a teammate's laptop issue, etc.
6. **By Sep 13:** Final submission — Idea Capture Template (if it needs updating), Pitch Deck, GitHub repo link, demo video.
