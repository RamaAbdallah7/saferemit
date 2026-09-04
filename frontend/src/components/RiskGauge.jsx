import { useEffect, useRef, useState } from "react";

const LABELS = { ALLOW: "ALLOW", STEP_UP: "STEP-UP", BLOCK: "BLOCK" };
const SUBTITLE = {
  ALLOW: "Cleared — no friction",
  STEP_UP: "Verify before proceeding",
  BLOCK: "Transaction stopped",
};

// 270-degree sweep, gap at the bottom.
const START = 135;
const SWEEP = 270;
const R = 108;
const C = 2 * Math.PI * R;
const ARC_LEN = (SWEEP / 360) * C;

function polar(cx, cy, r, deg) {
  const rad = ((deg - 90) * Math.PI) / 180;
  return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)];
}

export default function RiskGauge({ score, decision, running }) {
  const [shown, setShown] = useState(0);
  const raf = useRef();

  useEffect(() => {
    const target = score == null ? 0 : Math.max(0, Math.min(100, score));
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) {
      setShown(target);
      return;
    }
    const from = shown;
    const dur = 1100;
    const t0 = performance.now();
    cancelAnimationFrame(raf.current);
    const tick = (now) => {
      const p = Math.min(1, (now - t0) / dur);
      const eased = 1 - Math.pow(1 - p, 3);
      setShown(from + (target - from) * eased);
      if (p < 1) raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [score]);

  const state = decision ? decision.toLowerCase() : running ? "scanning" : "idle";
  const frac = shown / 100;
  const [sx, sy] = polar(140, 140, R, START);
  const largeArc = SWEEP > 180 ? 1 : 0;
  const [tex, tey] = polar(140, 140, R, START + SWEEP);
  const trackPath = `M ${sx} ${sy} A ${R} ${R} 0 ${largeArc} 1 ${tex} ${tey}`;
  const dash = `${ARC_LEN * frac} ${C}`;
  const bigNum = Math.round(shown);

  return (
    <div className={`gauge gauge-${state}`}>
      <svg viewBox="0 0 280 280" className="gauge-svg" role="img"
        aria-label={decision ? `Risk score ${bigNum} of 100, decision ${LABELS[decision]}` : "Awaiting assessment"}>
        <defs>
          <filter id="gaugeGlow" x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur stdDeviation="4" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* ticks */}
        {Array.from({ length: 28 }).map((_, i) => {
          const deg = START + (SWEEP / 27) * i;
          const [x1, y1] = polar(140, 140, R + 12, deg);
          const [x2, y2] = polar(140, 140, R + 18, deg);
          return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} className="gauge-tick" />;
        })}

        <path d={trackPath} className="gauge-track" fill="none" strokeWidth="10" strokeLinecap="round" />
        <path
          d={trackPath}
          className="gauge-fill"
          fill="none"
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={dash}
          filter="url(#gaugeGlow)"
          style={{ opacity: frac < 0.005 ? 0 : 1 }}
        />

        <text x="140" y="126" textAnchor="middle" className="gauge-num">{bigNum}</text>
        <text x="140" y="150" textAnchor="middle" className="gauge-scale">/ 100 risk</text>
        <text x="140" y="188" textAnchor="middle" className="gauge-verdict">
          {decision ? LABELS[decision] : running ? "SCANNING" : "STANDBY"}
        </text>
      </svg>
      <p className="gauge-sub">
        {decision ? SUBTITLE[decision] : running ? "Acquiring network signals…" : "Awaiting assessment run"}
      </p>
    </div>
  );
}
