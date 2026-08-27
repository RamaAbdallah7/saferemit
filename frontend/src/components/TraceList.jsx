import { motion, AnimatePresence } from "framer-motion";
import { STEP_LABELS } from "../api";

const listVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.14, delayChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 380, damping: 30 } },
};

const SOURCE_LABEL = {
  live: "live",
  mock: "mock",
  "mock-fallback": "mock (fallback)",
};

export default function TraceList({ trace, runKey }) {
  if (!trace || trace.length === 0) return null;

  return (
    <motion.ol
      key={runKey}
      className="trace"
      variants={listVariants}
      initial="hidden"
      animate="visible"
    >
      <AnimatePresence>
        {trace.map((entry, i) => {
          const pointsClass = entry.points > 0 ? "t-points" : "t-points zero";
          const pointsLabel = entry.api ? `+${entry.points} pts · score ${entry.running_score}` : "";
          const source = entry.signal?.source;
          return (
            <motion.li key={`${runKey}-${i}`} variants={itemVariants}>
              <div className="t-head">
                <span>
                  {STEP_LABELS[entry.step] || entry.step}
                  {source && (
                    <span className={`src-badge ${source}`} title={entry.signal?.live_error || ""}>
                      {SOURCE_LABEL[source] || source}
                    </span>
                  )}
                </span>
                <span className={pointsClass}>{pointsLabel}</span>
              </div>
              <div>{entry.reason}</div>
            </motion.li>
          );
        })}
      </AnimatePresence>
    </motion.ol>
  );
}
