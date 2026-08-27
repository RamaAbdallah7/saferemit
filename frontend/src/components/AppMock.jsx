import { motion, AnimatePresence } from "framer-motion";
import { PREVIEW_REQUESTS } from "../api";

function Field({ label, id, children }) {
  return (
    <div className="field">
      <label>{label}</label>
      <div className="value mono">{children}</div>
    </div>
  );
}

export default function AppMock({ scenario, onRun, running }) {
  const req = PREVIEW_REQUESTS[scenario?.id] || {};

  return (
    <section className="panel app-mock">
      <h2>
        Remittance App <span className="mock-tag">mock UI</span>
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

      <Field label="Phone number">{req.phone_number || "—"}</Field>
      <Field label="Action">{req.action_type || "—"}</Field>
      <Field label="Device">{req.device_fingerprint || "—"}</Field>
      <Field label="Claimed location">{req.claimed_location || "—"}</Field>

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
        This calls the same <code>/api/decide</code> endpoint a real remittance app would call — nothing here is faked at the UI layer.
      </p>
    </section>
  );
}
