# SafeRemit, explained in plain language

A walkthrough you can use to present the project or answer judge questions.
No code knowledge needed.

---

## The problem

Millions of migrant workers in the Gulf send money home every month. That
predictable flow is a magnet for two kinds of fraud:

1. **SIM-swap takeover.** A criminal convinces a phone carrier to move the
   victim's number to a new SIM card. Now the criminal receives the victim's
   one-time verification codes, resets the password, and empties the account.
2. **Mule-account onboarding.** Criminals open remittance accounts remotely using
   stolen or fake IDs, then use those accounts to move dirty money.

The checks apps use today — a texted code, a photo of an ID — can't catch either
in real time. The code goes to whoever holds the SIM. The ID photo is real; it
just isn't the person holding the phone.

## The idea

The mobile network knows things the app doesn't:

- Was this SIM swapped in the last few hours?
- Is the phone roaming, or outside the country the user claims to be in?
- Has the network ever seen this exact handset on this account before?

**SafeRemit is an AI agent that asks the network these questions in real time and
turns the answers into one decision:** let the transaction through, ask for extra
verification, or block it — in about 3–5 seconds, with a written reason.

Those network questions are asked through **CAMARA APIs** — a telecom-industry
standard — running on **Nokia's Network-as-Code** platform. That's the technology
this hackathon is about.

## How the agent thinks

It behaves like a careful fraud analyst, not a fixed checklist:

1. **Cheap checks first.** It checks the number and looks for a recent SIM swap —
   both at the same time. If it's a routine login and everything's clean, it
   stops there. No further questions, no delay.
2. **Escalate only when there's a reason.** If the action is risky (a transfer, a
   new-account signup) or an early signal looks wrong, it goes deeper: it checks
   whether the device is roaming and whether its real location matches the
   claimed one.
3. **The AI weighs the combination.** It hands all the signals to Google's Gemini
   model and asks it to reason like an analyst — because a single weak signal is
   usually noise, but *several* weak signals that fit a known fraud pattern is a
   strong case. Gemini returns its own verdict and a one-line explanation.
4. **Two opinions, reconciled.** SafeRemit also computes a transparent points
   score from a fixed rulebook. The final decision takes whichever of the two —
   the rules or the AI — is *stricter*, and if they disagree it flags the case
   for a human to review.

The screen shows every step: which network questions were asked, what came back,
how it added up, what the AI concluded, and the final call.

## What's real, and what's a prototype

Be upfront about this — judges respect it.

- **Real:** the agent, the decision logic, the AI reasoning, and the network
  calls. When you click "Run," it genuinely contacts Nokia's system and gets real
  answers.
- **Simulated:** it runs against Nokia's **test phone numbers**, each with a
  fixed, known profile — not real people's phones, because querying those needs
  carrier contracts. This is the sandbox every hackathon team uses.
- **Not yet tuned:** the exact risk weights (how many points a SIM swap adds) are
  sensible starting values, not numbers proven against real fraud data. A
  production version would learn these from real outcomes.

**In one sentence:** a genuine, working prototype that proves the mechanism
end-to-end — not a finished product that's been shown to stop fraud in the wild.

## The business

Sold to remittance apps, mobile-money operators and banks as a **fraud-decision
API** — one call at login, onboarding and transfer — priced per decision or per
account protected. It sits alongside their existing checks, not instead of them.
The same "fuse weak signals into one confident call" pattern also applies to
telecom fraud, insurance claims, and e-commerce account takeover.

## Why it fits this hackathon

- Uses **multiple CAMARA APIs** on Nokia Network-as-Code (SIM Swap, Device
  Status, Location Verification live; Number Verification wired).
- The **AI agent orchestrates** them as trusted real-time data sources and makes
  the decision — it isn't a button the user presses.
- Built entirely with tools from the hackathon's approved list (LangGraph +
  Google AI Studio / Gemini).
- Solves a **regionally specific, high-frequency** MENA problem.

## Three things to show in the demo

| Click | What it proves |
|---|---|
| **Clean login** | The agent stops after two quick checks — no friction for real users. |
| **SIM-swap takeover** | It escalates, calls three live network APIs, the AI agrees, → BLOCK with a clear reason. |
| **Custom request → "Network error → fallback"** | When a live call fails, the agent degrades gracefully and still decides. |
