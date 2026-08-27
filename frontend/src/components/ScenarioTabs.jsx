import { motion } from "framer-motion";

// The active pill's border slides between tabs using a shared layoutId —
// Framer Motion animates the transform automatically, no manual coordinate
// math needed. This is the kind of thing that's fiddly in plain CSS and
// nearly free with Framer Motion.
export default function ScenarioTabs({ scenarios, activeId, onSelect }) {
  return (
    <div className="scenario-tabs">
      {scenarios.map((s) => (
        <button
          key={s.id}
          className={activeId === s.id ? "active" : ""}
          onClick={() => onSelect(s.id)}
          style={{ position: "relative" }}
        >
          {activeId === s.id && (
            <motion.span
              layoutId="scenario-pill"
              transition={{ type: "spring", stiffness: 500, damping: 35 }}
              style={{
                position: "absolute",
                inset: 0,
                borderRadius: 999,
                border: "1px solid var(--accent)",
                background: "color-mix(in srgb, var(--accent) 12%, var(--panel))",
                zIndex: 0,
              }}
            />
          )}
          <span style={{ position: "relative", zIndex: 1 }}>{s.title}</span>
        </button>
      ))}
    </div>
  );
}
