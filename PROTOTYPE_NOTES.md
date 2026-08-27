# Prototype notes — read this before the Live Demo round

## What's real vs. simulated

- **Real:** the LangGraph agent, the escalation logic, the 0-100 rules score, the
  **Gemini analyst** and the rules-vs-AI reconciliation, the FastAPI backend, the
  React UI, and the 25-test `pytest` suite.
- **Live-or-mock:** the CAMARA clients (`backend/camara_apis/*.py`). Each calls
  the real Nokia Network-as-Code endpoint **when `NAC_API_KEY` is set**, else
  returns scenario-keyed canned data. A live call that errors/times out falls
  back to the mock and marks the signal `source: "mock-fallback"`.
- **Simulated network:** live calls hit Nokia's **Simulator** — fixed test
  MSISDNs, not real phones.

Graceful degradation on both the CAMARA calls and the LLM step is exactly what
the Resource & Tooling Guide tells you to build. `GET /api/health` reports the
current mode; every decision carries `camara_mode`, `signal_sources`, and an
`assessment` block (rules verdict, AI verdict, agreement).

## Live Nokia Network-as-Code status (2026-08-28)

Live mode is **on** and working. `.env` holds:

```
NAC_API_KEY=<application key from the portal Console>
NAC_BASE_URL=https://network-as-code.p-eu.apihub.nokia.io
NAC_RAPIDAPI_HOST=network-as-code.nokia.rapidapi.com
```

(`.env` is gitignored — never commit it.) Endpoints/bodies in each
`backend/camara_apis/*.py` `_live()` come verbatim from the portal Console
cURL snippets (API Playground → endpoint → Code Snippets), Simulator mode.

| CAMARA API | Endpoint | Live? |
|---|---|---|
| SIM Swap | `POST /passthrough/camara/v1/sim-swap/sim-swap/v0/check` (+ `/retrieve-date`) | ✅ live |
| Device Status – roaming | `POST /device-status/device-roaming-status/v1/retrieve` | ✅ live |
| Device Status – connectivity | `POST /device-status/v0/connectivity` | ✅ live |
| Location Verification | `POST /location-verification/v1/verify` | ✅ live |
| Number Verification | `POST /passthrough/camara/v1/number-verification/number-verification/v2/verify` | ⚠️ needs `Authorization: Bearer` (3-legged OAuth) — falls back to mock |

Test: `RUN_LIVE_CAMARA=1 python -m pytest backend/tests/test_live_camara.py -v`

**Number Verification** returns `{"detail":"Authorization header is missing"}`
without an OAuth token. In production the frontend carries the redirect; for
the demo it degrades to mock (documented, acceptable per the Tooling Guide).
TODO: try the NaC Authorization Server (client-credentials) to get a bearer
token for the Simulator, then pass it through `_nac.nac_post`.

### Simulator MSISDN map (from the NaC docs)

| Number | SIM Swap | Roaming | Location Verification |
|---|---|---|---|
| `+99999991001` | not swapped | not roaming | TRUE (in area) |
| `+99999991000` | swapped | roaming | FALSE (out of area) |
| `+99999991002` | swapped | roaming | PARTIAL |
| `+99999991003` | swapped | roaming | UNKNOWN |
| `+999999904xx` / `905xx` | — | HTTP 4xx/5xx | HTTP 4xx/5xx |

**In live mode the scripted scenarios use these:** `clean` runs against
`+99999991001` → **ALLOW**, `sim_swap_block` against `+99999991000` →
**BLOCK** — both as real CAMARA calls. `mismatch_stepup` has no single
simulator number that lands between the thresholds, so it stays on mock
data (labelled in the UI). The **Custom request** tab has one-click presets
for the simulator numbers, including `+99999990500` to demo the
graceful-degradation path.

**Number Verification** is CAMARA 3-legged OAuth — the subscriber's device
must open the consent URL over mobile data. Not doable server-side; it
degrades to mock (`signal_sources` will show `mock-fallback` for that one
step even in live mode). In production the mobile app carries the redirect.

## Where to tune the Framer Motion animation

The frontend was rebuilt on React + Vite specifically so this part is easy to iterate on with live reload (`npm run dev` in `frontend/`). Entry points:

- `frontend/src/components/TraceList.jsx` — `listVariants`/`itemVariants` control the staggered reveal of each reasoning step. `staggerChildren` (currently 0.14s) is the gap between steps appearing.
- `frontend/src/components/ReasoningPanel.jsx` — `RATIONALE_DELAY_S` times the rationale fade-in to land after the last trace item. If you change `staggerChildren` or the trace length assumption, update this too (it's a plain formula, not auto-derived, on purpose — easy to see and change).
- `frontend/src/components/DecisionBadge.jsx` — the spring transition on the badge itself, plus `useCountUp` for the risk-score number animation.
- `frontend/src/components/ScenarioTabs.jsx` — the sliding active-tab pill, done with a shared `layoutId` (Framer Motion animates the transform between tabs automatically).
- `frontend/src/styles.css` — colors/spacing/layout; unrelated to Framer Motion but often edited alongside it.

## The AI analyst (Gemini)

- Free key from https://aistudio.google.com/ → `.env` as `GEMINI_API_KEY`.
- `backend/agent/assessment.py` calls `gemini-3.6-flash` on the **escalation
  path only** (a clean login has no combination to reason about). It asks for a
  JSON verdict: `{decision, risk_score, reasoning}`.
- `finalize()` reconciles the LLM verdict with the rules score — **stricter of
  the two wins**, disagreements are flagged. Result carries `assessment.rules`,
  `assessment.ai`, `assessment.agreement`.
- `thinkingConfig.thinkingBudget` is kept low so the call is ~2-3s. On failure
  or no key, the decision is rules-only — safe to leave on for a live demo.

## Compliance checklist against the hackathon rules

- [x] **≥1 CAMARA API on Nokia Network-as-Code** — four wired; SIM Swap, Device
  Status, Location Verification run live.
- [x] **AI agent layer orchestrates the APIs as data sources, not buttons** —
  `orchestrator.py`: parallel checks, a conditional escalation edge, and an LLM
  reasoning node whose verdict drives the decision.
- [x] **Agent built only with approved tools** (guide PDF): **LangGraph** (§2) +
  **Google AI Studio / Gemini** (§3). Nothing else in the agent layer.
- [x] Matches the guide's **"Intermediate stack (Python)"**.
- [x] Follows the guide's demo tips: graceful degradation (CAMARA *and* LLM),
  cached data, reasoning trace on screen.
- [x] **Original code**, built in the Jul 1 – Sep 13 window.
- [x] **Theme 4** — Secure Fintech, Payments & Anti-Fraud.
- [x] Team size 2.
- [ ] **Still to do:** record the 3-minute demo video (`demo/DEMO_SCRIPT.md`);
  put the GitHub link in the final submission; (optional) deploy for a live link.
- [ ] **Check yourselves:** both members are 18+ and resident in an Arab League
  country or Türkiye.
