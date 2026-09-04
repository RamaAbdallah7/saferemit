import { motion } from "framer-motion";

// The active pill slides between tabs using a shared layoutId — Framer
// Motion animates the transform automatically, no manual coordinate math.
export default function ScenarioTabs({ scenarios, activeId, onSelect }) {
  return (
    <div className="scenario-tabs">
      {scenarios.map((s) => (
        <button
          key={s.id}
          className={activeId === s.id ? "active" : ""}
          onClick={() => onSelect(s.id)}
          type="button"
        >
          {activeId === s.id && (
            <motion.span
              layoutId="scenario-pill"
              className="scenario-pill"
              transition={{ type: "spring", stiffness: 480, damping: 34 }}
            />
          )}
          <span className="scenario-tab-label">{s.title}</span>
        </button>
      ))}
    </div>
  );
}
