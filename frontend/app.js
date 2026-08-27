(function () {
  const tabsEl = document.getElementById("scenarioTabs");
  const descEl = document.getElementById("scenarioDesc");
  const fPhone = document.getElementById("fPhone");
  const fAction = document.getElementById("fAction");
  const fDevice = document.getElementById("fDevice");
  const fLocation = document.getElementById("fLocation");
  const runBtn = document.getElementById("runBtn");
  const badgeEl = document.getElementById("decisionBadge");
  const traceEl = document.getElementById("traceList");
  const rationaleBox = document.getElementById("rationaleBox");
  const rationaleText = document.getElementById("rationaleText");
  const rationaleSource = document.getElementById("rationaleSource");

  // Kept in sync with backend/scenarios.py for the field preview;
  // the actual decision always comes from the live API call.
  const PREVIEW_REQUESTS = {
    clean: { phone_number: "+971501234567", action_type: "login", device_fingerprint: "device-fp-known-abc123", claimed_location: "Dubai, UAE" },
    sim_swap_block: { phone_number: "+971501234567", action_type: "login", device_fingerprint: "device-fp-unknown-xyz999", claimed_location: "Dubai, UAE" },
    mismatch_stepup: { phone_number: "+971509876543", action_type: "onboarding", device_fingerprint: "device-fp-unknown-new777", claimed_location: "Cairo, Egypt" },
  };

  let scenarios = [];
  let activeScenario = null;

  function selectScenario(id) {
    activeScenario = id;
    [...tabsEl.children].forEach((btn) => btn.classList.toggle("active", btn.dataset.id === id));
    const s = scenarios.find((x) => x.id === id);
    descEl.textContent = s ? s.description : "";
    const req = PREVIEW_REQUESTS[id] || {};
    fPhone.textContent = req.phone_number || "—";
    fAction.textContent = req.action_type || "—";
    fDevice.textContent = req.device_fingerprint || "—";
    fLocation.textContent = req.claimed_location || "—";
    resetResult();
  }

  function resetResult() {
    badgeEl.className = "decision-badge";
    badgeEl.innerHTML = '<span class="badge-text">Awaiting run…</span>';
    traceEl.innerHTML = "";
    rationaleBox.hidden = true;
  }

  async function loadScenarios() {
    const res = await fetch("/api/scenarios");
    const data = await res.json();
    scenarios = data.scenarios;
    tabsEl.innerHTML = "";
    scenarios.forEach((s, i) => {
      const btn = document.createElement("button");
      btn.textContent = s.title;
      btn.dataset.id = s.id;
      btn.addEventListener("click", () => selectScenario(s.id));
      tabsEl.appendChild(btn);
      if (i === 0) selectScenario(s.id);
    });
  }

  function stepLabel(step) {
    return {
      number_verification: "Number Verification",
      sim_swap: "SIM Swap",
      escalation_decision: "Escalation decision",
      device_status: "Device Status",
      location_verification: "Location Verification",
    }[step] || step;
  }

  function renderTrace(trace) {
    traceEl.innerHTML = "";
    trace.forEach((entry, i) => {
      const li = document.createElement("li");
      li.style.animationDelay = `${i * 140}ms`;
      const pointsClass = entry.points > 0 ? "t-points" : "t-points zero";
      const pointsLabel = entry.api ? `+${entry.points} pts · score ${entry.running_score}` : "";
      li.innerHTML = `
        <div class="t-head"><span>${stepLabel(entry.step)}</span><span class="${pointsClass}">${pointsLabel}</span></div>
        <div>${entry.reason}</div>
      `;
      traceEl.appendChild(li);
    });
  }

  async function runDecision() {
    if (!activeScenario) return;
    runBtn.disabled = true;
    runBtn.textContent = "Running…";
    resetResult();
    try {
      const res = await fetch("/api/decide", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario: activeScenario }),
      });
      if (!res.ok) throw new Error(`API returned ${res.status}`);
      const result = await res.json();

      const decisionClass = result.decision.toLowerCase();
      badgeEl.className = `decision-badge ${decisionClass}`;
      badgeEl.innerHTML = `<span class="badge-text">${result.decision.replace("_", "-")} · risk score ${result.risk_score}/100</span>`;

      renderTrace(result.trace);

      rationaleBox.hidden = false;
      rationaleText.textContent = result.rationale;
      rationaleSource.textContent = `(${result.rationale_source})`;
    } catch (err) {
      badgeEl.className = "decision-badge block";
      badgeEl.innerHTML = `<span class="badge-text">Request failed — is the backend running?</span>`;
      console.error(err);
    } finally {
      runBtn.disabled = false;
      runBtn.textContent = "Run SafeRemit decision";
    }
  }

  runBtn.addEventListener("click", runDecision);
  loadScenarios();
})();
