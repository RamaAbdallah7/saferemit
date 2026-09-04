import { useEffect, useRef } from "react";

// Topic imagery, not decoration: value ("money") travels as light along a
// remittance corridor from sender to receiver. A faint vertical line at 62%
// is the trust boundary / checkpoint. Most packets are gold and pass; every
// few seconds a red one is intercepted at the boundary — it stalls, flares,
// and dies. Honours prefers-reduced-motion with a single static frame.
export default function MoneyFlow({ height = 320, intercept = true }) {
  const ref = useRef(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    let w, h, dpr, raf, packets, t = 0, lastRed = 0;
    const BOUNDARY = 0.62;

    function resize() {
      dpr = Math.min(2, window.devicePixelRatio || 1);
      w = canvas.clientWidth;
      h = canvas.clientHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    // shallow descending arc that lives in the lower band of the canvas so
    // it never fights the headline sitting above it
    function pointAt(p) {
      const x = p * w;
      const midLift = Math.sin(p * Math.PI) * (h * 0.22);
      const y = h * 0.46 + p * (h * 0.34) - midLift;
      return [x, y];
    }

    function spawn(red = false) {
      packets.push({
        p: -0.04 - Math.random() * 0.05,
        speed: 0.0022 + Math.random() * 0.0016,
        r: red ? 0 : 1,
        red,
        dead: false,
        stall: 0,
        size: red ? 3 : 1.6 + Math.random() * 1.6,
      });
    }

    function frame() {
      t += 1;
      ctx.clearRect(0, 0, w, h);

      // corridor line
      ctx.strokeStyle = "rgba(217,183,121,0.16)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let i = 0; i <= 60; i++) {
        const [x, y] = pointAt(i / 60);
        i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
      }
      ctx.stroke();

      // trust boundary
      const bx = BOUNDARY * w;
      ctx.strokeStyle = "rgba(239,233,224,0.14)";
      ctx.setLineDash([3, 5]);
      ctx.beginPath();
      ctx.moveTo(bx, h * 0.06);
      ctx.lineTo(bx, h * 0.94);
      ctx.stroke();
      ctx.setLineDash([]);

      if (packets.length < 26 && t % 10 === 0) spawn(false);
      if (intercept && t - lastRed > 320) {
        spawn(true);
        lastRed = t;
      }

      for (const pk of packets) {
        if (pk.dead) continue;
        if (pk.red && pk.p >= BOUNDARY - 0.005 && pk.stall < 60) {
          pk.stall += 1;
        } else {
          pk.p += pk.speed;
        }
        if (pk.red && pk.stall >= 60) {
          pk.dead = true;
          continue;
        }
        if (pk.p > 1.05) pk.dead = true;

        const [x, y] = pointAt(Math.min(1, Math.max(0, pk.p)));
        const flare = pk.red ? 0.4 + (pk.stall / 60) * 0.9 : 0;
        const col = pk.red ? "200,80,60" : "217,183,121";
        const glow = pk.red ? 14 + flare * 20 : 9;

        ctx.shadowBlur = glow;
        ctx.shadowColor = `rgba(${col},0.9)`;
        ctx.fillStyle = `rgba(${col},${pk.red ? 0.95 : 0.85})`;
        ctx.beginPath();
        ctx.arc(x, y, pk.size + flare * 2, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;

        // trailing streak
        const [px, py] = pointAt(Math.min(1, Math.max(0, pk.p - 0.03)));
        const grad = ctx.createLinearGradient(px, py, x, y);
        grad.addColorStop(0, `rgba(${col},0)`);
        grad.addColorStop(1, `rgba(${col},${pk.red ? 0.5 : 0.35})`);
        ctx.strokeStyle = grad;
        ctx.lineWidth = pk.size;
        ctx.beginPath();
        ctx.moveTo(px, py);
        ctx.lineTo(x, y);
        ctx.stroke();
      }

      packets = packets.filter((p) => !p.dead);
      if (!reduce) raf = requestAnimationFrame(frame);
    }

    resize();
    packets = [];
    for (let i = 0; i < 14; i++) spawn(false), (packets[i].p = Math.random());
    frame();
    const onR = () => resize();
    window.addEventListener("resize", onR);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", onR);
    };
  }, [intercept]);

  return <canvas ref={ref} className="money-flow" style={{ height }} aria-hidden="true" />;
}
