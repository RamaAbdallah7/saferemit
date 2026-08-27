"""
CAMARA Number Verification API client (live-or-mock).

Live: networkAsCode SDK -> client.number_verification.verify(phone_number=...)
     CAMARA response: { "devicePhoneNumberVerified": bool }

NOTE: CAMARA Number Verification is a 3-legged flow - the subscriber's
device normally completes an OAuth authorization on-network before the
verify call. Server-to-server it works only against the NaC simulated
network (API Playground test numbers). If the live call needs consent it
raises and we fall back to the mock - which is an acceptable, documented
degradation per the Tooling Guide.

Without NAC_API_KEY (or if the live call fails) this returns the
scenario-keyed mock below.
"""
from ._nac import NacError, as_dict, call, client, live_enabled

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
        resp = call(lambda: client().number_verification.verify(phone_number=phone_number))
        data = as_dict(resp)
        verified = data.get("device_phone_number_verified")
        if verified is None:
            verified = data.get("devicePhoneNumberVerified")
        return {
            "api": "number_verification",
            "phone_number": phone_number,
            "verified": bool(verified),
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
