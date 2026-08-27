"""
CAMARA Number Verification API client (live-or-mock).

Live (Nokia NaC apihub, Simulator mode):
  POST /passthrough/camara/v1/number-verification/number-verification/v2/verify
    body { "phoneNumber": "+..." }  -> { "devicePhoneNumberVerified": bool }

NOTE: in production CAMARA Number Verification is a 3-legged flow (the
subscriber's device authorizes on-network first). The Simulator accepts a
plain phoneNumber; if a live call ever needs consent it raises and we
fall back to the mock - documented, acceptable degradation per the
Tooling Guide.

Without NAC_API_KEY (or if the live call fails) this returns the
scenario-keyed mock below.
"""
from ._nac import NacError, live_enabled, nac_post

_VERIFY = "/passthrough/camara/v1/number-verification/number-verification/v2/verify"

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
        data = nac_post(_VERIFY, {"phoneNumber": phone_number})
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
