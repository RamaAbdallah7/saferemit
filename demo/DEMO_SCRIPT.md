# 3-minute demo video script

Matches the submission requirement: "A screen-recorded video (max 3 minutes) demonstrating the working prototype, API calls, and UI/UX."

**Setup before recording**
1. `cp .env.example .env` and set `NAC_API_KEY` (see `PROTOTYPE_NOTES.md`) so the header shows **LIVE · Nokia NaC**.
2. `cd frontend && npm run build` then, from the project root, `python -m uvicorn backend.app:app`.
3. Open `http://127.0.0.1:8000` full-screen, close other tabs/notifications.
4. Do one dry run of each scenario first — live calls take ~2-3s, so know the pacing.

---

### 0:00–0:18 — Hook + problem (voiceover over the UI, no clicking yet)

> "Every payday, migrant workers across the GCC send money home — a predictable, high-value flow that fraud rings target two ways: SIM-swap account takeover, and synthetic mule onboarding. Static OTP and document checks can't catch either in real time. SafeRemit reads the signals only the network can see."

Point at the green **LIVE · Nokia NaC** pill in the header.

### 0:18–0:52 — Scenario 1: Clean login  ·  ALLOW

Click **Clean login** → **Run SafeRemit decision**.

> "A returning user, usual device. The agent runs the two cheap checks — Number Verification and SIM Swap — in parallel. Both clean, so it makes an efficiency call and stops: no device or location lookup. That decision — which API is worth pulling — is what makes this an agent, not a checklist."

Point at the `LIVE` badge on SIM Swap, the fast-path note, the **ALLOW · risk score 0** badge.

### 0:52–1:40 — Scenario 2: SIM-swap takeover  ·  BLOCK

Click **SIM-swap takeover attempt** → **Run**.

> "Same account. The SIM was swapped minutes ago from an unrecognized device. SIM Swap comes back positive — a real call to Nokia's network — so the agent escalates, pulls Device Status and Location Verification in parallel, and fuses all four signals: risk 100, block, with a plain-language reason a fraud analyst can act on."

Point at each `LIVE` badge as the trace fills, then the red **BLOCK** verdict and the rationale.

### 1:40–2:20 — Scenario 3: Mismatched onboarding  ·  STEP-UP

Click **Mismatched onboarding** → **Run**.

> "A brand-new account onboarding — a sensitive action, so the agent proactively pulls every signal. Roaming, unrecognized device, location mismatch: not damning enough to block, exactly the case for step-up verification — protect the user without killing a legitimate signup."

Point at the amber **STEP-UP** badge. (This scenario runs on cached signal data — note the `mock` badges — because no single simulator number lands between the thresholds; see `PROTOTYPE_NOTES.md`.)

### 2:20–2:45 — Custom request + graceful degradation

Click **Custom request** → the **Network error → fallback** preset → **Run**.

> "And when a live call fails — here the gateway returns a 500 — the agent degrades to cached data and still decides. It never stalls mid-transaction."

### 2:45–3:00 — Close (screen: pitch deck architecture diagram, or the UI)

> "A LangGraph agent orchestrating CAMARA APIs on Nokia Network-as-Code, Gemini writing the rationale — the tooling guide's own recommended stack. Licensed per decision to remittance apps, operators and banks. SafeRemit — stopping remittance fraud before the money moves. Thank you."

---

**Filming tips:** keep the cursor deliberate — pause ~1s on each trace line so judges can read it. If a live call is slow on the day, the mock fallback still produces the right verdict, so the demo is safe either way.
