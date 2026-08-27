"""
CAMARA Location Verification API client (live-or-mock).

Live (Nokia NaC apihub, Simulator mode):
  POST /location-verification/v1/verify
    body { "device": { "phoneNumber": "+..." },
           "area": { "areaType": "CIRCLE",
                     "center": { "latitude": <lat>, "longitude": <lon> },
                     "radius": <metres> } }
    -> { "verificationResult": "TRUE"|"FALSE"|"PARTIAL"|"UNKNOWN",
         "matchRate": int (only when PARTIAL) }

The remittance app knows a claimed location as text ("Dubai, UAE"); a
real deployment geocodes that. For the demo we resolve the handful of
scenario cities from GAZETTEER below.

Without NAC_API_KEY (or if the live call fails) this returns the
scenario-keyed mock.
"""
from ._nac import NacError, live_enabled, nac_post

_VERIFY = "/location-verification/v1/verify"

# Minimal geocoder for the demo scenarios. A real deployment calls a
# geocoding service here.
GAZETTEER = {
    "dubai, uae": (25.2048, 55.2708),
    "abu dhabi, uae": (24.4539, 54.3773),
    "cairo, egypt": (30.0444, 31.2357),
    "riyadh, saudi arabia": (24.7136, 46.6753),
}
DEFAULT_RADIUS_M = 5000

SCENARIOS = {
    "clean": {"verification_result": "TRUE", "match_rate": 97},
    "sim_swap_block": {"verification_result": "PARTIAL", "match_rate": 54},
    "mismatch_stepup": {"verification_result": "FALSE", "match_rate": 12},
}


class LocationVerificationClient:
    """CAMARA Location Verification client."""

    def verify(self, phone_number: str, claimed_location: str, scenario: str = "clean") -> dict:
        coords = GAZETTEER.get(claimed_location.strip().lower())
        if live_enabled() and coords is not None:
            try:
                return self._live(phone_number, claimed_location, coords)
            except NacError as exc:
                return self._mock(phone_number, claimed_location, scenario,
                                  source="mock-fallback", live_error=str(exc))
        return self._mock(phone_number, claimed_location, scenario, source="mock")

    def _live(self, phone_number: str, claimed_location: str, coords: tuple[float, float]) -> dict:
        lat, lon = coords
        data = nac_post(_VERIFY, {
            "device": {"phoneNumber": phone_number},
            "area": {
                "areaType": "CIRCLE",
                "center": {"latitude": lat, "longitude": lon},
                "radius": DEFAULT_RADIUS_M,
            },
        })
        return {
            "api": "location_verification",
            "phone_number": phone_number,
            "claimed_location": claimed_location,
            "verification_result": data.get("verificationResult", "UNKNOWN"),
            "match_rate": data.get("matchRate", 0),
            "source": "live",
        }

    def _mock(self, phone_number: str, claimed_location: str, scenario: str,
              *, source: str, live_error: str | None = None) -> dict:
        data = SCENARIOS.get(scenario, SCENARIOS["clean"])
        result = {
            "api": "location_verification",
            "phone_number": phone_number,
            "claimed_location": claimed_location,
            "verification_result": data["verification_result"],
            "match_rate": data["match_rate"],
            "source": source,
        }
        if live_error:
            result["live_error"] = live_error
        return result
