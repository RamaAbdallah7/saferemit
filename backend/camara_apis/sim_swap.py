"""
CAMARA SIM Swap API client (live-or-mock).

Live: networkAsCode SDK -> client.sim_swap.check(phone_number, max_age)
     CAMARA response: { "swapped": bool }

Without NAC_API_KEY (or if the live call fails) this returns the
scenario-keyed mock below - see backend/camara_apis/_nac.py.
"""
from datetime import datetime, timedelta, timezone

from ._nac import NacError, as_dict, call, client, live_enabled

SCENARIOS = {
    "clean": {
        "swapped": False,
        "latest_sim_change": None,
    },
    "sim_swap_block": {
        "swapped": True,
        # swapped 40 minutes ago - well inside the high-risk window
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
        resp = call(lambda: client().sim_swap.check(
            phone_number=phone_number, max_age=max_age_hours,
        ))
        data = as_dict(resp)
        return {
            "api": "sim_swap",
            "phone_number": phone_number,
            "swapped": bool(data.get("swapped")),
            "latest_sim_change": data.get("latest_sim_change") or data.get("latestSimChange"),
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
