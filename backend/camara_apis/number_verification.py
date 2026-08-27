"""
CAMARA Number Verification API client (live-or-mock).

Live endpoint (Nokia Network-as-Code):
  POST {base}/camara/number-verification/v0/verify
  Body: { "phoneNumber": "+9715XXXXXXXX" }
  CAMARA response: { "devicePhoneNumberVerified": true|false }

Without NAC_API_KEY (or if the live call fails) this returns the
scenario-keyed mock below — see backend/camara_apis/_nac.py.
"""
from ._nac import NacError, live_enabled, nac_post

SCENARIOS = {
    "clean": {"verified": True},
    "sim_swap_block": {"verified": True},   # number itself checks out; SIM swap is the red flag
    "mismatch_stepup": {"verified": True},
}


class NumberVerificationClient:
    """CAMARA Number Verification client."""

    def verify(self, phone_number: str, scenario: str = "clean") -> dict:
        if live_enabled():
            try:
                return self._live(phone_number)
            except NacError as exc:
                return self._mock(phone_number, scenario,
                                  source="mock-fallback", live_error=str(exc))
        return self._mock(phone_number, scenario, source="mock")

    def _live(self, phone_number: str) -> dict:
        data = nac_post(
            "/camara/number-verification/v0/verify",
            {"phoneNumber": phone_number},
        )
        return {
            "api": "number_verification",
            "phone_number": phone_number,
            "verified": bool(data.get("devicePhoneNumberVerified")),
            "source": "live",
        }

    def _mock(self, phone_number: str, scenario: str,
              *, source: str, live_error: str | None = None) -> dict:
        data = SCENARIOS.get(scenario, SCENARIOS["clean"])
        result = {
            "api": "number_verification",
            "phone_number": phone_number,
            "verified": data["verified"],
            "source": source,
        }
        if live_error:
            result["live_error"] = live_error
        return result
