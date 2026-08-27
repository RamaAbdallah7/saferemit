import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const LABELS = { ALLOW: "ALLOW", STEP_UP: "STEP-UP", BLOCK: "BLOCK" };

function useCountUp(target, durationMs = 600) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    if (target == null) {
      setValue(0);
      return;
    }
    let raf;
    const start = performance.now();
    const from = 0;
    const tick = (now) => {
      const t = Math.min(1, (now - start) / durationMs);
      const eased = 1 - Math.pow(1 - t, 3); // ease-out cubic
      setValue(Math.round(from + (target - from) * eased));
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, durationMs]);
  return value;
}

export default function DecisionBadge({ result }) {
  const score = useCountUp(result?.risk_score);

  return (
    <AnimatePresence mode="wait">
      {!result ? (
        <motion.div
          key="empty"
          className="decision-badge"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <span className="badge-text">Awaiting run…</span>
        </motion.div>
      ) : (
        <motion.div
          key={result.decision + result.risk_score}
          className={`decision-badge ${result.decision.toLowerCase()}`}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ type: "spring", stiffness: 420, damping: 28 }}
        >
          <span className="badge-text">
            {LABELS[result.decision] || result.decision} · risk score {score}/100
          </span>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
