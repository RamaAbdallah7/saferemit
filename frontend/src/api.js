export async function fetchScenarios() {
  const res = await fetch("/api/scenarios");
  if (!res.ok) throw new Error(`GET /api/scenarios -> ${res.status}`);
  const data = await res.json();
  return data.scenarios;
}

export async function decide(scenarioId) {
  const res = await fetch("/api/decide", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scenario: scenarioId }),
  });
  if (!res.ok) throw new Error(`POST /api/decide -> ${res.status}`);
  return res.json();
}

// Mirrors backend/scenarios.py — used only to preview form fields before a
// run. The actual decision always comes from the live API call above.
export const PREVIEW_REQUESTS = {
  clean: {
    phone_number: "+971501234567",
    action_type: "login",
    device_fingerprint: "device-fp-known-abc123",
    claimed_location: "Dubai, UAE",
  },
  sim_swap_block: {
    phone_number: "+971501234567",
    action_type: "login",
    device_fingerprint: "device-fp-unknown-xyz999",
    claimed_location: "Dubai, UAE",
  },
  mismatch_stepup: {
    phone_number: "+971509876543",
    action_type: "onboarding",
    device_fingerprint: "device-fp-unknown-new777",
    claimed_location: "Cairo, Egypt",
  },
};

export const STEP_LABELS = {
  number_verification: "Number Verification",
  sim_swap: "SIM Swap",
  escalation_decision: "Escalation decision",
  device_status: "Device Status",
  location_verification: "Location Verification",
};
