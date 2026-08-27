import { motion, AnimatePresence } from "framer-motion";
import { PREVIEW_REQUESTS, ACTION_TYPES } from "../api";

function ReadOnlyField({ label, children }) {
  return (
    <div className="field">
      <label>{label}</label>
      <div className="value mono">{children}</div>
    </div>
  );
}

function EditField({ label, value, onChange, placeholder }) {
  return (
    <div className="field">
      <label>{label}</label>
      <input
        className="value mono input"
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

export default function AppMock({ scenario, isCustom, customReq, onCustomChange, onRun, running }) {
  const preview = PREVIEW_REQUESTS[scenario?.id] || {};
  const setField = (k) => (v) => onCustomChange({ ...customReq, [k]: v });

  return (
    <section className="panel app-mock">
      <h2>
        Remittance App <span className="mock-tag">{isCustom ? "editable" : "mock UI"}</span>
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

      {isCustom ? (
        <>
          <EditField label="Phone number" value={customReq.phone_number}
            onChange={setField("phone_number")} placeholder="+99999991000" />
          <div className="field">
            <label>Action</label>
            <div className="seg">
              {ACTION_TYPES.map((a) => (
                <button
                  key={a}
                  type="button"
                  className={customReq.action_type === a ? "on" : ""}
                  onClick={() => setField("action_type")(a)}
                >
                  {a}
                </button>
              ))}
            </div>
          </div>
          <EditField label="Device fingerprint" value={customReq.device_fingerprint}
            onChange={setField("device_fingerprint")} placeholder="device-fp-…" />
          <EditField label="Claimed location" value={customReq.claimed_location}
            onChange={setField("claimed_location")} placeholder="Dubai, UAE" />
        </>
      ) : (
        <>
          <ReadOnlyField label="Phone number">{preview.phone_number || "—"}</ReadOnlyField>
          <ReadOnlyField label="Action">{preview.action_type || "—"}</ReadOnlyField>
          <ReadOnlyField label="Device">{preview.device_fingerprint || "—"}</ReadOnlyField>
          <ReadOnlyField label="Claimed location">{preview.claimed_location || "—"}</ReadOnlyField>
        </>
      )}

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
