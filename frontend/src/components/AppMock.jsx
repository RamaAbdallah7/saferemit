import { motion, AnimatePresence } from "framer-motion";
import { ACTION_TYPES, CUSTOM_PRESETS } from "../api";

function EditField({ label, value, onChange, placeholder }) {
  return (
    <div className="field">
      <label>{label}</label>
      <input
        className="value mono input"
        value={value ?? ""}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

export default function AppMock({ scenario, form, dirty, onChange, onRun, running }) {
  const set = (k) => (v) => onChange({ [k]: v });

  return (
    <section className="panel app-mock">
      <h2>
        Remittance App <span className="mock-tag">editable</span>
      </h2>

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

      <div className="presets">
        {CUSTOM_PRESETS.map((p) => (
          <button key={p.label} type="button" className="preset" title={p.note}
            onClick={() => onChange(p.req)}>
            {p.label}
          </button>
        ))}
      </div>

      <EditField label="Phone number" value={form.phone_number}
        onChange={set("phone_number")} placeholder="+99999991000" />

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
      </div>

      <EditField label="Device fingerprint" value={form.device_fingerprint}
        onChange={set("device_fingerprint")} placeholder="device-fp-..." />
      <EditField label="Claimed location" value={form.claimed_location}
        onChange={set("claimed_location")} placeholder="Dubai, UAE" />

      <motion.button
        className="run-btn"
        onClick={onRun}
        disabled={running}
        whileTap={{ scale: 0.98 }}
        whileHover={{ scale: running ? 1 : 1.01 }}
      >
        {running ? "Running…" : "Run SafeRemit decision"}
      </motion.button>

      <p className="hint">
        {dirty && scenario?.id !== "__custom__"
          ? "Edited — this runs as a custom request against the live agent."
          : "This calls the same /api/decide endpoint a real remittance app would call — nothing here is faked at the UI layer."}
      </p>
    </section>
  );
}
