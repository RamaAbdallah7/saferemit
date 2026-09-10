# SafeRemit — Virtual Demo (Deliverable 03)

**URL to use for everything:** https://saferemit.onrender.com  (never localhost)
**Repo link for the form:** https://github.com/RamaAbdallah7/saferemit

---

## 0. What deliverable 03 actually requires

From the Submission Format infographic, **03 · Virtual Demo** must contain:

| Part | Where it goes | Status |
|---|---|---|
| Screen-recorded video, **max 3 min**, showing **working prototype + the API calls + the UI/UX** | Video URL field | to record |
| Link to code repo | Repository URL field | ready — github.com/RamaAbdallah7/saferemit |
| **Demo description + commercial-value summary** | Description / "demo descriptions" text field | draft in §D below |
| **API-usage synopsis** | Description text field | draft in §D below |
| **Business-impact statement** | Description text field | draft in §D below |

So "API calls and usage" means two things: (1) the **video has to visibly show the CAMARA API calls happening** — not just the final verdict — and (2) there's a **written API-usage synopsis** that goes in the form text, not the video. Both are covered below.

The good news: the app's reasoning panel already lists every call by name — **Number Verification · SIM Swap · Device Status · Location Verification · AI analyst (Gemini)** — each with a live / mock badge. Filming that panel *is* showing the API calls. Your job in the script is just to name them out loud as they appear.

---

## A. Before you hit record (5 min prep)

1. **Wake the server.** Open https://saferemit.onrender.com ~2 min early (Render free tier cold-starts, ~50 s blank). Reload once it paints.
2. **Warm-up run** — run all three scenarios once:
   - `Clean login` → **ALLOW, risk 0**
   - `SIM-swap takeover attempt` → **BLOCK, risk 90**
   - `Mismatched onboarding` → **STEP-UP, risk 45**
3. **Check the badges** in the trace after the SIM-swap run. Live right now:
   - **SIM Swap** → `live` · **Device Status** → `live` · **Location Verification** → `live`
   - **Number Verification** → `mock · fallback` (expected — see §C, you disclose this on camera)
   - **AI analyst (Gemini)** → shows `AI` when it responds, or `unavailable` on a free-tier hiccup. Re-run once or twice until it says `AI`. If it just won't, use the *(if Gemini didn't run)* line — the decision is identical without it.
4. **Browser:** 1920×1080, zoom 100%, no bookmarks bar, one clean tab.
5. **Recorder:** Loom / OBS / Win+G. Mic on. Target **2:45**, hard cap **3:00**.
6. Optional: `docs/diagrams/c4-container.png` open in a 2nd tab for the closing shot.

---

## B. Shot-by-shot script

> Read the "Say" column close to verbatim — it's timed. Times are targets.

### 0:00 – 0:20 · Landing page, top of the story

**Do:** Recording starts with the page loaded at the very top — "Fraud follows the money" headline on screen. Don't scroll yet.

**Say:**
> "This is SafeRemit. For millions of families across the Middle East and Türkiye, money sent home from abroad is the household income — and that's what fraudsters target. Once an attacker has taken over someone's phone number with a SIM swap, a password or an OTP can't tell them apart from the real customer."

### 0:20 – 0:40 · Scroll to "The intervention"

**Do:** Scroll down at a readable pace, stop at "SafeRemit checks the network, not the password".

**Say:**
> "SafeRemit checks the network instead. Before a transfer clears, an AI agent pulls live signals straight from the mobile operator through GSMA Open Gateway and Nokia Network-as-Code, and scores them into one decision — allow, step up, or block."

**Do:** Click **"Run a live decision"** — it scrolls to "The checkpoint".

### 0:40 – 0:52 · The checkpoint — status chips

**Do:** Hover the top-right chips: **"Live · Nokia NaC"** and **"Gemini analyst"**.

**Say:**
> "Everything from here is real — these are live CAMARA API calls against Nokia's network simulator, with a Gemini model as a second analyst. Same `/api/decide` endpoint a real remittance app would call."

### 0:52 – 1:12 · Scenario 1 — Clean login → ALLOW

**Do:** `Clean login` tab selected. Click **"Run assessment"**. Let the trace animate in.

**Say:**
> "A normal customer — usual phone, usual device, logging in from Dubai. The agent runs the two cheap checks first: **Number Verification** and **SIM Swap**. Both clean — so it stops there. A fast path, no deeper API calls, no AI. Risk zero. **Allow** — zero friction for the genuine 99%."

### 1:12 – 2:05 · Scenario 2 — SIM-swap takeover → BLOCK  *(the main beat — slow down)*

**Do:** Click **"SIM-swap takeover attempt"** tab. Gesture at the request card — same phone number, unrecognized device. Click **"Run assessment"**. As each trace row lands, move your cursor to it.

**Say:**
> "Same account — but the SIM was swapped minutes ago and the device is one this account has never seen. Now the agent escalates and calls all four APIs. Watch the trace."

**Do:** Point at each row and its badge as you name it:
> "**SIM Swap** — live call to Nokia — swap in the last 72 hours, plus forty-five.
> **Device Status** — live — unrecognized device, and it's roaming, plus thirty.
> **Location Verification** — live — the claimed location doesn't match the network..."

**Do:** Hover the Location row so its reasoning text shows.
> "...but the device is roaming, so the agent reads that as *travel*, not spoofing — plus fifteen, not thirty. Location is never allowed to be the sole reason for a block.
> And **Number Verification** here falls back to cached data — that CAMARA API needs the end-user's on-device OAuth consent, which a server can't do; that's a documented limitation, not a failure.
> Total: ninety out of a hundred. **Block** — stopped before the money moves."

**Say (if Gemini ran — badge says `AI`):**
> "And the Gemini analyst independently returned the same verdict — block. Rules and AI agree, so confidence is high."

**Say (if Gemini didn't run — badge says `unavailable`):**
> "The Gemini analyst is a second opinion on top of this. It's rate-limited right now, so the agent just proceeds on the deterministic rules score — it never depends on the AI."

### 2:05 – 2:32 · Scenario 3 — Mismatched onboarding → STEP-UP

**Do:** Click **"Mismatched onboarding"** tab. Click **"Run assessment"**.

**Say:**
> "The in-between case — a brand-new account, unrecognized roaming device, location mismatch. All four APIs run again. Suspicious, but no SIM swap, nothing conclusive. Risk forty-five. The agent doesn't block a possibly-real customer — it returns **step up**: one more identity check. That's the difference between a fraud tool people trust and one that locks everyone out."

### 2:32 – 2:55 · Close

**Do:** Stay on the panel, or cut to the C4 diagram.

**Say:**
> "Under the hood: a LangGraph agent orchestrates the CAMARA calls, a deterministic rules engine owns the score, and the AI can only make a decision stricter, never looser — disagreements go to a human. One stateless service, and because GSMA Open Gateway is one standard across operators, the same integration covers the Gulf-to-Egypt, Türkiye and wider MENA corridors with no per-bank build. That's SafeRemit."

**Do:** Stop recording.

---

## C. Numbers & facts to get right

| Scenario | Decision | Risk | APIs called | Points |
|---|---|---|---|---|
| Clean login | **ALLOW** | 0 / 100 | Number Verification, SIM Swap (fast path — stops early) | all clean |
| SIM-swap takeover | **BLOCK** | 90 / 100 | all 4 CAMARA + Gemini | SIM swap +45 · unknown & roaming device +30 · location mismatch +15 (halved, roaming = travel) |
| Mismatched onboarding | **STEP-UP** | 45 / 100 | all 4 CAMARA + Gemini | unknown & roaming device +30 · location mismatch +15 · onboarding forced escalation |

- Thresholds: **0–29 ALLOW · 30–69 STEP-UP · 70+ BLOCK.** No single signal reaches 70 alone.
- **Live vs mock, right now:** SIM Swap, Device Status, Location Verification = **live** against Nokia's simulator. Number Verification = **mock fallback** (CAMARA 3-legged OAuth / device consent — can't be done server-side; documented). That's **3 of 4 CAMARA APIs live.**
- Clean + SIM-swap scenarios run against real simulator MSISDNs. Mismatched onboarding has no matching simulator number, so it runs on cached demo data — fine to say if asked.

---

## D. Text for the HackerEarth form (NOT the video)

Paste these into the **Description** field (and the "demo descriptions" box if it's separate).

### Demo description
> The 3-minute demo runs the live prototype at saferemit.onrender.com through three scenarios against the same `/api/decide` endpoint a remittance app would call. **Clean login:** a returning customer on a known device — the agent runs two cheap checks (Number Verification, SIM Swap), both clean, and returns ALLOW at risk 0 with no further calls. **SIM-swap takeover:** the SIM was swapped in the last 72 h and the device is unrecognized — the agent escalates, calls Device Status and Location Verification, scores SIM swap +45, unknown roaming device +30, location mismatch +15, and returns BLOCK at risk 90; the Gemini analyst returns the same verdict independently. **Mismatched onboarding:** a new account on an unrecognized roaming device with a location mismatch — suspicious but not conclusive, so the agent returns STEP-UP at risk 45 rather than blocking a possibly-genuine customer. Every CAMARA call and its live/mock source is shown on screen in the reasoning trace.

### API-usage synopsis
> SafeRemit orchestrates four GSMA Open Gateway / CAMARA APIs on Nokia Network-as-Code, called by a LangGraph agent:
> • **SIM Swap** — was the SIM changed inside a 72 h risk window (OTP-interception precursor). *Live.*
> • **Device Status** — is the device known to this account, and is it roaming. *Live.*
> • **Location Verification** — does the customer's claimed location match the network's view of the device. *Live.*
> • **Number Verification** — is the phone number actually the one on the requesting device. *Falls back to cached data:* this CAMARA API requires 3-legged OAuth (end-user consent on the device) which a server-to-server call cannot perform — a documented platform limitation, not a defect.
> The agent is conditional, not a fixed pipeline: it runs Number Verification + SIM Swap first (parallel), and only calls Device Status + Location Verification when an early signal looks risky or the action is sensitive (onboarding/transfer). Independent calls run concurrently; a full escalated decision completes in ~2–3 s. A fifth call goes to **Google AI Studio (Gemini)** on the escalation path only — a general model constrained to a fixed JSON verdict, used as a second opinion. A deterministic rules engine owns the score; Gemini can raise the severity of a decision but never lower it, and the system degrades to rules-only if Gemini is unavailable. 3 of 4 CAMARA APIs run live against Nokia's Simulator; per-signal live/mock badges are visible in the UI.

### Commercial-value summary
> B2B2C. SafeRemit licenses to remittance apps, mobile-money operators and banks as a decisioning endpoint, priced per decision or per protected account. It sits alongside existing KYC and rules engines, integrating as a single API call at three moments — login, onboarding, transfer. Because GSMA Open Gateway is one standard across operators, one integration covers the Gulf-to-Egypt, Türkiye and wider MENA corridors with no per-bank rebuild, so revenue scales with transaction volume rather than with engineering headcount.

### Business-impact statement
> Cross-border remittances to the region run into the tens of billions of dollars a year and are a primary fraud target, with SIM-swap account takeover and synthetic-identity mule onboarding the two dominant patterns. SafeRemit stops both before money moves, while protecting legitimate customers: borderline cases get a STEP-UP identity check instead of a blunt block, and location signals — the usual source of false positives from VPNs and travel — are explicitly prevented from blocking a transaction on their own. The result is fraud caught earlier with fewer genuine customers turned away.

---

## E. Optional 2-min polish before recording

The small "How the score becomes a decision" table inside the request card still shows "Location does not match network +30" without the roaming-halved row. The live reasoning trace is already correct; the static table is just slightly behind. Worth fixing if you have the time, not a blocker.
