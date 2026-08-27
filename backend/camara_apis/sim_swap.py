"""
Mock for the CAMARA SIM Swap API (retrieve-date + check operations).

Real endpoint (Nokia Network-as-Code):
  POST https://network-as-code.p-eu.rapidapi.com/camara/sim-swap/v0/check
  Body: { "phoneNumber": "+9715XXXXXXXX", "maxAge": 240 }
  Docs: https://developer.networkascode.nokia.io/

Real response shape (CAMARA spec):
  { "swapped": true|false }
  or, for retrieve-date:
  { "latestSimChange": "2026-08-26T10:15:00Z" }

TODO (swap-in): replace `SimSwapClient.check` body with a call to the NaC
SDK client, e.g.:
    from network_as_code import NetworkAsCodeClient
    client = NetworkAsCodeClient(token=os.environ["NAC_API_KEY"])
    device = client.devices.get(phone_number=phone_number)
    return device.sim_swap.check(max_age=240)
"""
from datetime import datetime, timedelta, timezone

SCENARIOS = {
    "clean": {
        "swapped": False,
        "latest_sim_change": None,
    },
    "sim_swap_block": {
        "swapped": True,
        # swapped 40 minutes ago — well inside the high-risk window
        "latest_sim_change": (datetime.now(timezone.utc) - timedelta(minutes=40)).isoformat(),
    },
    "mismatch_stepup": {
        "swapped": False,
        "latest_sim_change": None,
    },
}


class SimSwapClient:
    """Mock CAMARA SIM Swap client."""

    def check(self, phone_number: str, max_age_hours: int = 72, scenario: str = "clean") -> dict:
        data = SCENARIOS.get(scenario, SCENARIOS["clean"])
        return {
            "api": "sim_swap",
            "phone_number": phone_number,
            "swapped": data["swapped"],
            "latest_sim_change": data["latest_sim_change"],
            "checked_window_hours": max_age_hours,
        }
