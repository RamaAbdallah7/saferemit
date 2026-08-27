# 3-minute demo video script

Matches the submission requirement: "A screen-recorded video (max 3 minutes) demonstrating the working prototype, API calls, and UI/UX."

**Setup before recording:** run the backend (`uvicorn backend.app:app`), open `http://127.0.0.1:8000` full-screen, close other tabs/notifications.

---

### 0:00–0:20 — Hook + problem (voiceover over the UI, no clicking yet)

> "Every payday, migrant workers across the GCC send remittances home — and that predictable flow is exactly what fraud rings target. Two patterns dominate: SIM-swap account takeover, and synthetic mule onboarding. Static OTP and document checks can't catch either in real time. SafeRemit can."

### 0:20–0:55 — Scenario 1: Clean login (click "Clean login" tab → "Run SafeRemit decision")

> "Here's a returning user logging in normally. Watch the agent: it checks Number Verification, checks for a recent SIM swap — both clean — so it makes an efficiency call: no need to pull device or location data. That's the agent deciding which CAMARA API is worth calling, not just running a fixed checklist."

Let the trace animate, point at the ALLOW badge and the risk score.

### 0:55–1:45 — Scenario 2: SIM-swap takeover (click "SIM-swap takeover attempt" → run)

> "Same account. This time the SIM was swapped 40 minutes ago from an unrecognized device. The agent immediately escalates — pulls Device Status and Location Verification too — and fuses all four signals into one decision: block, with a plain-language reason a fraud analyst can act on immediately, not just a score."

Point at each trace line as it appears, then the BLOCK badge + rationale text.

### 1:45–2:30 — Scenario 3: Mismatched onboarding (click "Mismatched onboarding" → run)

> "Now a brand-new account onboarding — that alone is a sensitive action, so the agent proactively pulls every signal, even before anything looks wrong. It finds a roaming, unrecognized device and a location mismatch — not damning enough to block outright, but exactly the case where step-up verification protects the user without killing a legitimate signup."

Point at STEP_UP badge.

### 2:30–2:50 — Architecture + business model (screen: architecture diagram from pitch deck, or just narrate over the UI)

> "Under the hood: a LangGraph agent orchestrates four CAMARA APIs on Nokia Network-as-Code, with Gemini generating the analyst-facing rationale. It's B2B2C — licensed to remittance apps, mobile-money operators, and banks per decision, and the same pattern generalizes to telco fraud and e-commerce account takeover."

### 2:50–3:00 — Close

> "SafeRemit — stopping remittance fraud before the money moves, with zero added friction for everyone else. Thank you."

---

**Filming tips:** do a dry run once before recording so the trace animation timing feels natural on camera. Keep your cursor deliberate — pause on each trace line for ~1 second so judges can actually read it.
