import { motion, AnimatePresence } from "framer-motion";
import RiskGauge from "./RiskGauge";
import TraceList from "./TraceList";

// Rationale reveal is delayed to land just after the last staggered trace
// item finishes (see TraceList's staggerChildren/delayChildren timing).
const RATIONALE_DELAY_S = 0.1 + 6 * 0.14 + 0.3;

const LABEL = { ALLOW: "ALLOW", STEP_UP: "STEP-UP", BLOCK: "BLOCK" };

function Assessment({ assessment }) {
  if (!assessment) return null;
  const { mode, rules, ai, agreement } = assessment;

  return (
    <div className="assessment">
      <div className="assessment-row">
        <span className="a-label">Rules engine</span>
        <span className={`a-verdict ${rules.decision.toLowerCase()}`}>
          {LABEL[rules.decision]} · {rules.risk_score}
        </span>
      </div>
      {ai ? (
        <>
          <div className="assessment-row">
            <span className="a-label">AI analyst · Gemini</span>
            <span className={`a-verdict ${ai.decision.toLowerCase()}`}>
              {LABEL[ai.decision]} · {ai.risk_score}
            </span>
          </div>
          <p className={`a-note ${agreement ? "agree" : "disagree"}`}>
            {agreement
              ? "Both engines agree — confidence is high."
              : "Split call — the agent took the stricter decision and flagged it for review."}
          </p>
        </>
      ) : (
        <p className="a-note">{mode}</p>
      )}
    </div>
  );
}

export default function ReasoningPanel({ result, runKey, running }) {
  return (
    <section className="panel reasoning">
      <div className="panel-kicker">Assessment</div>

      <RiskGauge
        score={result?.risk_score ?? null}
        decision={result?.decision ?? null}
        running={running}
      />

      <TraceList trace={result?.trace} runKey={runKey} />

      <AnimatePresence>
        {result && (
          <motion.div
            className="rationale"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1, transition: { delay: RATIONALE_DELAY_S, duration: 0.35 } }}
            exit={{ opacity: 0 }}
          >
            <Assessment assessment={result.assessment} />
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
