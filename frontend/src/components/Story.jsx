import { motion } from "framer-motion";
import MoneyFlow from "./MoneyFlow";
import StatCounter from "./StatCounter";

const rise = {
  hidden: { opacity: 0, y: 22 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.22, 0.7, 0.2, 1] } },
};

const ATTACK = [
  {
    k: "01",
    t: "The SIM is swapped",
    d: "An attacker convinces the carrier to move the victim's number onto a SIM they control. No malware, no phishing link — a phone call. It can finish in minutes.",
    glyph: (
      <>
        <rect x="8" y="4" width="20" height="32" rx="3" />
        <path d="M18 30h0" />
        <path d="M34 12l6 6-6 6" />
        <path d="M40 18H24" />
      </>
    ),
  },
  {
    k: "02",
    t: "The one-time code is intercepted",
    d: "Every SMS and OTP the bank sends now arrives on the attacker's phone. The victim's handset just shows 'No Service'.",
    glyph: (
      <>
        <path d="M6 20c8-10 28-10 36 0" />
        <path d="M12 24c6-6 18-6 24 0" />
        <circle cx="24" cy="30" r="2.5" />
        <path d="M30 6l8 8M38 6l-8 8" />
      </>
    ),
  },
  {
    k: "03",
    t: "The transfer is ‘authorised’",
    d: "Valid login. Valid code. Known account. Every check the bank can see says yes — so the remittance is released.",
    glyph: (
      <>
        <path d="M6 24l7 7 15-16" />
        <path d="M24 30h18" />
        <path d="M24 36h12" />
      </>
    ),
  },
  {
    k: "04",
    t: "The money is gone",
    d: "Funds land in a rented mule account and are pulled straight back out. Often the first sign anything is wrong is the family saying the money never arrived.",
    glyph: (
      <>
        <circle cx="16" cy="20" r="9" />
        <path d="M16 15v10M13 18h6" />
        <path d="M28 20h14M36 14l6 6-6 6" />
      </>
    ),
  },
];

export default function Story({ onStart }) {
  return (
    <div className="story">
      {/* ---- Act 1: the stakes ---- */}
      <section className="act hero">
        <MoneyFlow height={230} />
        <div className="act-inner">
          <motion.p className="kicker" variants={rise} initial="hidden" animate="show">
            Cross-border remittance fraud
          </motion.p>
          <motion.h1 variants={rise} initial="hidden" animate="show" transition={{ delay: 0.08 }}>
            For millions of families across the Middle East and Türkiye, money sent
            home from abroad is the income. <em>Fraud follows the money.</em>
          </motion.h1>
          <motion.p
            className="lede"
            variants={rise}
            initial="hidden"
            animate="show"
            transition={{ delay: 0.16 }}
          >
            SafeRemit is an AI agent that reads the mobile network itself — SIM
            status, device, location — and stops a transfer the moment it looks
            stolen, before the money leaves.
          </motion.p>
        </div>
      </section>

      <section className="act stats">
        <motion.div
          className="stat-row"
          variants={rise}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, amount: 0.4 }}
        >
          <StatCounter
            prefix="$"
            value={22.7}
            decimals={1}
            suffix="B"
            label="received by Egypt alone in 2024 — the world's 7th-largest recipient, and for millions of families the main household income"
            source="World Bank, 2024"
            icon={
              <>
                <ellipse cx="20" cy="11" rx="12" ry="4.5" />
                <path d="M8 11v7c0 2.5 5.4 4.5 12 4.5s12-2 12-4.5v-7" />
                <path d="M8 18v7c0 2.5 5.4 4.5 12 4.5s12-2 12-4.5v-7" />
                <path d="M8 25v7c0 2.5 5.4 4.5 12 4.5s12-2 12-4.5v-7" />
              </>
            }
          />
          <StatCounter
            prefix="~$"
            value={3000}
            suffix=""
            label="stolen from a typical SIM-swap victim across the Middle East, Türkiye and Africa — from a swap that costs the attacker as little as $10"
            source="Kaspersky"
            icon={
              <>
                <path d="M9 5h15l7 7v23a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z" />
                <rect x="14" y="18" width="12" height="10" rx="1.5" />
                <path d="M20 18v10M14 23h12" />
              </>
            }
          />
          <StatCounter
            value={40000}
            suffix="+"
            label="UAE residents lost money to a scam in 2024 — and only 9% of those who lost money got all of it back"
            source="BioCatch UAE survey, 2024"
            icon={
              <>
                <path d="M20 3l13 5v9c0 9-5.5 14.5-13 20-7.5-5.5-13-11-13-20V8z" />
                <path d="M13 12l14 16" />
              </>
            }
          />
        </motion.div>
      </section>

      {/* ---- Act 2: the attack ---- */}
      <section className="act attack">
        <motion.h2 variants={rise} initial="hidden" whileInView="show" viewport={{ once: true }}>
          How one transfer gets stolen
        </motion.h2>
        <ol className="attack-steps">
          {ATTACK.map((s, i) => (
            <motion.li
              key={s.k}
              variants={rise}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true, amount: 0.5 }}
              transition={{ delay: i * 0.05 }}
            >
              <svg viewBox="0 0 48 40" className="attack-glyph" aria-hidden="true">
                {s.glyph}
              </svg>
              <div>
                <span className="step-k">{s.k}</span>
                <h3>{s.t}</h3>
                <p>{s.d}</p>
              </div>
            </motion.li>
          ))}
        </ol>
        <motion.p
          className="attack-close"
          variants={rise}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
        >
          A password or an OTP cannot tell the real customer from the attacker
          holding their number. <em>The network can.</em>
        </motion.p>
      </section>

      {/* ---- Act 3: the intervention ---- */}
      <section className="act intervene">
        <motion.div variants={rise} initial="hidden" whileInView="show" viewport={{ once: true }}>
          <p className="kicker">The intervention</p>
          <h2>SafeRemit checks the network, not the password</h2>
          <p className="lede">
            Before a transfer clears, the agent pulls four live signals from the
            mobile operator through GSMA Open Gateway / Nokia Network-as-Code —
            <span className="mono"> SIM&nbsp;Swap</span>,
            <span className="mono"> Number&nbsp;Verification</span>,
            <span className="mono"> Device&nbsp;Status</span>,
            <span className="mono"> Location</span> — and an orchestration agent
            scores them into one decision: allow, step&#8209;up, or block. GSMA Open
            Gateway is one standard across operators, so the same integration covers
            the Gulf-to-Egypt, Türkiye and wider MENA corridors without a per-bank build.
          </p>
          <button className="start-btn" onClick={onStart} type="button">
            Run a live decision
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
          </button>
        </motion.div>
      </section>
    </div>
  );
}
