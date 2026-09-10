import { STEP_LABELS } from "../api";

/**
 * Draws each CAMARA call as a bar on a shared time axis. Bars that overlap
 * ran concurrently — this is the visual proof of real parallel API
 * activity (Number Verification + SIM Swap together, then Device Status +
 * Location together). Timings come straight from the /api/decide response
 * `timing` block, measured server-side.
 */
export default function ApiTimeline({ timing }) {
  if (!timing || !Array.isArray(timing.calls) || timing.calls.length === 0) return null;

  const span = Math.max(1, ...timing.calls.map((c) => c.end_ms));

  return (
    <div className="api-timeline">
      <div className="atl-head">
        <span className="mono">CAMARA calls · {timing.total_ms} ms end-to-end</span>
        <span className="atl-note mono">overlapping bars ran in parallel</span>
      </div>
      {timing.calls.map((c, i) => {
        const left = (c.start_ms / span) * 100;
        const width = Math.max(1.5, ((c.end_ms - c.start_ms) / span) * 100);
        return (
          <div className="atl-row" key={i}>
            <span className="atl-name mono">{STEP_LABELS[c.api] || c.api}</span>
            <span className="atl-track">
              <span
                className={`atl-bar ${c.source === "live" ? "live" : "mock"}`}
                style={{ left: `${left}%`, width: `${width}%` }}
              />
            </span>
            <span className="atl-ms mono">
              {c.ms} ms · {c.source}
            </span>
          </div>
        );
      })}
    </div>
  );
}
