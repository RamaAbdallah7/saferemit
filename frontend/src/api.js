export async function fetchHealth() {
  const res = await fetch("/api/health");
  if (!res.ok) throw new Error(`GET /api/health -> ${res.status}`);
  return res.json();
}

export async function fetchScenarios() {
  const res = await fetch("/api/scenarios");
  if (!res.ok) throw new Error(`GET /api/scenarios -> ${res.status}`);
  const data = await res.json();
  return data.scenarios;
}

// Accepts either a scenario id (string) or a full custom request object
// ({ phone_number, action_type, device_fingerprint, claimed_location }).
export async function decide(scenarioOrRequest) {
  const body =
    typeof scenarioOrRequest === "string"
      ? { scenario: scenarioOrRequest }
      : scenarioOrRequest;
  const res = await fetch("/api/decide", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = "";
    try {
      detail = (await res.json()).detail || "";
    } catch {
      /* ignore */
    }
    throw new Error(`POST /api/decide -> ${res.status}${detail ? ` (${detail})` : ""}`);
  }
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

// Starting point for the editable "Custom request" mode. The simulator
// MSISDN +99999991000 is what the Nokia NaC docs use for live test calls.
export const CUSTOM_DEFAULT = {
  phone_number: "+99999991000",
  action_type: "transfer",
  device_fingerprint: "device-fp-known-abc123",
  claimed_location: "Dubai, UAE",
};

export const ACTION_TYPES = ["login", "onboarding", "transfer"];

export const STEP_LABELS = {
  number_verification: "Number Verification",
  sim_swap: "SIM Swap",
  escalation_decision: "Escalation decision",
  device_status: "Device Status",
  location_verification: "Location Verification",
};
