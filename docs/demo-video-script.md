# SafeRemit — Virtual Demo script (Deliverable 03)

**URL:** https://saferemit.onrender.com — stay on this one tab the whole recording.
**Repo:** https://github.com/RamaAbdallah7/saferemit

This walkthrough is a presentation layer (the numbers are simulated so it runs
anywhere in ~3 minutes). The working prototype that makes real, live CAMARA
calls is a separate page at `/app` — it isn't part of this recording, but its
existence and how to verify it belong in the submission's written Description,
not the video. See `docs/compliance-audit.html` for what deliverable 03 requires
in the Description field (API-usage synopsis, commercial-value summary,
business-impact statement).

**Before recording:** open the site a couple of minutes early so Render is warm.
Do one full click-through as a dry run.

---

*Bracketed = what you click. Everything else = what you say, casually.*

**[Opening screen]**

"Okay so — this is SafeRemit. Quick bit of context: for a lot of families across the Middle East and Türkiye, the money a relative sends home from abroad basically *is* the household income. And that makes it a target. The number one attack is a SIM swap — someone takes over your phone number, and now every OTP the bank sends goes to *them*. The login's right, the code's right… nothing looks wrong to the bank.

So let's just follow one family and watch what happens."

**[Click "Follow one family"]**

**[Next — the two people]**

"This is Ahmed, he works in Dubai. Every month he sends money to his mum, Mariam, in İstanbul. Same amount, same person — that's his normal pattern."

**[Next — Ahmed's app]**

"Here's his app. You can see his last three transfers, all going to 'Mum'."

**[Next — the fake message]**

"Tonight he gets a message that looks like it's from his provider, and he enters his login. So now the attacker has everything a bank actually checks."

**[Next — the transfer]**

"And the attacker starts a transfer — twelve thousand dirhams, to a brand-new account. And notice: to the app, nothing about this looks wrong."

**[Next — the network check, let the animation play out]**

"But before the money moves, SafeRemit checks the network. It pulls signals from the mobile operator through CAMARA APIs on Nokia — and here's what it finds. SIM was swapped two hours ago. New device. Location doesn't match. Each one alone is minor, but together…"

**[Next — Gemini]**

"…Gemini reads the whole combination and explains it in plain language. And the important part — Gemini *recommends*, it doesn't decide anything."

**[Next — the risk score]**

"That gets scored. Ninety-one out of a hundred — high risk."

**[Next — the bank's view]**

"Now the bank sees this. And instead of just blocking Ahmed —"

**[Click "Request verification"]**

"— it brings in someone he already trusts."

**[Next — Mariam's phone]**

"Mariam gets one question: did Ahmed tell you he was sending this? She knows he didn't."

**[Click "No — not right"]**

**[Next — the protected screen]**

"And that's it. Transfer paused. Twelve thousand dirhams stays with the family it was for."

**[Next — the without/with comparison]**

"Quick side by side — without SafeRemit, the money's just gone and the family finds out later. With it, the network catches what the password couldn't."

---

**[Next — the sandbox, "Try any combination"]**

"Okay, and this part you can actually play with. Every network signal is a toggle here. Let me show two."

**[Click the "Customer is travelling" preset]**

"So this is someone genuinely abroad — roaming, location doesn't match. But it stays ALLOW. Because on a roaming phone, that's just travel, not fraud."

**[Click the "SIM-swap takeover" preset]**

"Now add a recent SIM swap and a new device — and it jumps to PAUSE. So no single signal ever blocks a transfer. It always takes a combination."

---

**[Next — architecture, "How it fits together"]**

"And here's how it actually fits together — request comes in, SafeRemit pulls the network signals through Nokia and CAMARA, Gemini explains the combination, the risk engine scores it, and the bank always makes the final call."

**[End — talk to camera, or land on the close screen]**

"So — that's SafeRemit. Sometimes the account is correct, the password is correct, the OTP is correct… but the network can still tell you something changed. CAMARA, Nokia Network-as-Code, and Gemini, tied together by one risk engine a bank could actually deploy. Thanks for watching."

---

## Numbers to have memorized, if asked in Q&A

| Scenario | Decision | Risk | CAMARA live? |
|---|---|---|---|
| Clean login | ALLOW | 0 | Number Verification + SIM Swap (fast path) |
| SIM-swap takeover | BLOCK | ~90 | SIM Swap, Device Status, Location = live; Number Verification = mock (device-side 3-legged flow) |
| Mismatched onboarding | STEP-UP | 45 | all 4 checked, Location on mock simulator number |

Thresholds: 0–30 allow, 31–70 step-up, 71–100 block. No single signal exceeds ~45,
so a block always needs at least two corroborating signals.

**If asked "is it really live":** the answer lives in the submission's written
Description, not on camera — see the "How to verify it's real" section there
(`/api/health`, the `/api/decide` `timing` block showing parallel calls, Nokia's
own Network-as-Code analytics, the public source).
