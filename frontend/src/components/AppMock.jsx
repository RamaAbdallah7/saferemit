import { motion, AnimatePresence } from "framer-motion";
import { ACTION_TYPES, CUSTOM_PRESETS } from "../api";

function EditField({ label, value, onChange, placeholder, hint }) {
  return (
    <div className="field">
      <label>{label}</label>
      <input
        className="value mono input"
        value={value ?? ""}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
      />
      {hint && <p className="field-hint">{hint}</p>}
    </div>
  );
}

const ACTION_HINT = {
  login: "Account access. Takes the fast path (SIM + number only) unless an early signal is already bad.",
  onboarding: "New account. Always escalates to the device + location checks — mule accounts are opened, not logged into.",
  transfer: "The payout itself. Always escalates — this is the money moving, so it gets the deepest look.",
};

export default function AppMock({ scenario, form, dirty, onChange, onRun, running }) {
  const set = (k) => (v) => onChange({ [k]: v });

  return (
    <section className="panel intake">
      <div className="panel-kicker">Intake</div>
      <h2>Remittance request</h2>

      <p className="intake-lead">
        These four inputs are what a remittance app already holds the moment a
        transfer is submitted. SafeRemit adds the mobile network's own view of
        the same customer on top.
      </p>

      <AnimatePresence mode="wait">
        <motion.p
          key={scenario?.id}
          className="scenario-desc"
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 4 }}
          transition={{ duration: 0.18 }}
        >
          {scenario?.description}
        </motion.p>
      </AnimatePresence>

      <div className="preset-group">
        <span className="preset-label">Nokia NaC simulator numbers — each lands on a known outcome</span>
        <div className="presets">
          {CUSTOM_PRESETS.map((p) => (
            <button key={p.label} type="button" className="preset" title={p.note}
              onClick={() => onChange(p.req)}>
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <EditField label="Phone number" value={form.phone_number}
        onChange={set("phone_number")} placeholder="+99999991000"
        hint="The only key the CAMARA APIs accept. Defaults to a Nokia NaC simulator number (…1001) because the sandbox only returns real, repeatable signals for those; type another simulator number for its scripted outcome, or any real number and the agent falls back to cached data." />

      <div className="field">
        <label>Action</label>
        <div className="seg">
          {ACTION_TYPES.map((a) => (
            <button key={a} type="button"
              className={form.action_type === a ? "on" : ""}
              onClick={() => set("action_type")(a)}>
              {a}
            </button>
          ))}
        </div>
        <p className="field-hint">{ACTION_HINT[form.action_type]}</p>
      </div>

      <EditField label="Device fingerprint" value={form.device_fingerprint}
        onChange={set("device_fingerprint")} placeholder="device-fp-..."
        hint="A device this account hasn't used before adds +20 to the risk score — takeover almost always comes from a new handset." />
      <EditField label="Claimed location" value={form.claimed_location}
        onChange={set("claimed_location")} placeholder="Dubai, UAE"
        hint="Checked against where the SIM actually is on the network. Full mismatch adds +30, partial +15." />

      <motion.button
        className={`run-btn ${running ? "is-running" : ""}`}
        onClick={onRun}
        disabled={running}
        whileTap={{ scale: 0.985 }}
      >
        <span>{running ? "Assessing…" : "Run assessment"}</span>
      </motion.button>

      <details className="score-key">
        <summary>How the score becomes a decision</summary>
        <table>
          <tbody>
            <tr><td>SIM swapped in last 72h</td><td>+45</td></tr>
            <tr><td>Number not verified on the device</td><td>+35</td></tr>
            <tr><td>Location does not match network</td><td>+30</td></tr>
            <tr><td>Unknown device</td><td>+20</td></tr>
            <tr><td>Location partially matches</td><td>+15</td></tr>
            <tr><td>Device roaming</td><td>+10</td></tr>
          </tbody>
        </table>
        <p>
          <span className="k-allow">0–29 allow</span> ·
          <span className="k-step"> 30–69 step&#8209;up</span> ·
          <span className="k-block"> 70+ block</span>. Gemini reviews the same
          signals on the escalation path; the agent takes whichever verdict is stricter.
        </p>
      </details>

      <p className="hint">
        {dirty && scenario?.id !== "__custom__"
          ? "Edited — this runs as a custom request against the live agent."
          : "Calls the same /api/decide endpoint a real remittance app would call — nothing here is faked at the UI layer."}
      </p>
    </section>
  );
}
