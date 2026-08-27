"""
CAMARA SIM Swap API client (live-or-mock).

Live endpoint (Nokia Network-as-Code):
  POST {base}/camara/sim-swap/v0/check
  Body: { "phoneNumber": "+9715XXXXXXXX", "maxAge": <hours> }
  CAMARA response: { "swapped": true|false }

Without NAC_API_KEY (or if the live call fails) this returns the
scenario-keyed mock below — see backend/camara_apis/_nac.py for why.
"""
from datetime import datetime, timedelta, timezone

from ._nac import NacError, live_enabled, nac_post

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
    """CAMARA SIM Swap client."""

    def check(self, phone_number: str, max_age_hours: int = 72, scenario: str = "clean") -> dict:
        if live_enabled():
            try:
                return self._live(phone_number, max_age_hours)
            except NacError as exc:
                return self._mock(phone_number, max_age_hours, scenario,
                                  source="mock-fallback", live_error=str(exc))
        return self._mock(phone_number, max_age_hours, scenario, source="mock")

    def _live(self, phone_number: str, max_age_hours: int) -> dict:
        data = nac_post(
            "/camara/sim-swap/v0/check",
            {"phoneNumber": phone_number, "maxAge": max_age_hours},
        )
        return {
            "api": "sim_swap",
            "phone_number": phone_number,
            "swapped": bool(data.get("swapped")),
            "latest_sim_change": data.get("latestSimChange"),
            "checked_window_hours": max_age_hours,
            "source": "live",
        }

    def _mock(self, phone_number: str, max_age_hours: int, scenario: str,
              *, source: str, live_error: str | None = None) -> dict:
        data = SCENARIOS.get(scenario, SCENARIOS["clean"])
        result = {
            "api": "sim_swap",
            "phone_number": phone_number,
            "swapped": data["swapped"],
            "latest_sim_change": data["latest_sim_change"],
            "checked_window_hours": max_age_hours,
            "source": source,
        }
        if live_error:
            result["live_error"] = live_error
        return result
