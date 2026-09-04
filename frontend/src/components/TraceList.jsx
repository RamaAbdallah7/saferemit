import { motion } from "framer-motion";
import { STEP_LABELS } from "../api";

const listVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.14, delayChildren: 0.1 } },
};

const itemVariants = {
  hidden: { opacity: 0, x: -12 },
  visible: { opacity: 1, x: 0, transition: { type: "spring", stiffness: 360, damping: 28 } },
};

const SOURCE_LABEL = {
  live: "live",
  mock: "mock",
  "mock-fallback": "mock · fallback",
  gemini: "AI",
  "gemini-unavailable": "unavailable",
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
      {trace.map((entry, i) => {
        const scored = entry.api;
        const pointsClass = entry.points > 0 ? "t-points hot" : "t-points";
        const pointsLabel = scored
          ? `+${entry.points} · ${Math.min(100, entry.running_score)}`
          : "";
        const source = entry.signal?.source;
        return (
          <motion.li key={`${runKey}-${i}`} variants={itemVariants} className={scored ? "scored" : ""}>
            <span className="t-node" aria-hidden="true" />
            <div className="t-body">
              <div className="t-head">
                <span className="t-name">
                  {STEP_LABELS[entry.step] || entry.step}
                  {source && (
                    <span className={`src-badge ${source}`} title={entry.signal?.live_error || ""}>
                      {SOURCE_LABEL[source] || source}
                    </span>
                  )}
                </span>
                {pointsLabel && <span className={pointsClass}>{pointsLabel}</span>}
              </div>
              <div className="t-reason">{entry.reason}</div>
            </div>
          </motion.li>
        );
      })}
    </motion.ol>
  );
}
