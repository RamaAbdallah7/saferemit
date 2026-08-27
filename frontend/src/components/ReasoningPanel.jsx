import { motion, AnimatePresence } from "framer-motion";
import DecisionBadge from "./DecisionBadge";
import TraceList from "./TraceList";

// Rationale reveal is delayed to land just after the last staggered trace
// item finishes (see TraceList's staggerChildren/delayChildren timing) —
// tune RATIONALE_DELAY_S alongside those values if you change the stagger.
const RATIONALE_DELAY_S = 0.1 + 4 * 0.14 + 0.25;

export default function ReasoningPanel({ result, runKey }) {
  return (
    <section className="panel reasoning">
      <h2>Agent Reasoning</h2>
      <DecisionBadge result={result} />
      <TraceList trace={result?.trace} runKey={runKey} />

      <AnimatePresence>
        {result && (
          <motion.div
            className="rationale"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1, transition: { delay: RATIONALE_DELAY_S, duration: 0.35 } }}
            exit={{ opacity: 0 }}
          >
            <div className="rationale-label">
              Rationale <span className="mono">({result.rationale_source})</span>
            </div>
            <p>{result.rationale}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}
