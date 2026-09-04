import { useEffect, useRef, useState } from "react";

// Counts from 0 to `value` the first time it scrolls into view.
export default function StatCounter({ prefix = "", value, decimals = 0, suffix = "", label, source, icon }) {
  const [n, setN] = useState(0);
  const ref = useRef(null);
  const done = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const run = () => {
      if (done.current) return;
      done.current = true;
      if (reduce) return setN(value);
      const dur = 1500;
      const t0 = performance.now();
      const tick = (now) => {
        const p = Math.min(1, (now - t0) / dur);
        const eased = 1 - Math.pow(1 - p, 3);
        setN(value * eased);
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };

    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => e.isIntersecting && run()),
      { threshold: 0.5 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, [value]);

  return (
    <div className="stat" ref={ref}>
      {icon && (
        <svg viewBox="0 0 40 40" className="stat-icon" aria-hidden="true">
          {icon}
        </svg>
      )}
      <div className="stat-n">
        {prefix}
        {n.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}
        {suffix}
      </div>
      <div className="stat-l">{label}</div>
      {source && <div className="stat-src">{source}</div>}
    </div>
  );
}
