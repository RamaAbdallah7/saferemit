"""
CAMARA Device Status API client (live-or-mock).

Live endpoint (Nokia Network-as-Code):
  POST {base}/camara/device-status/v0/roaming
  Body: { "device": { "phoneNumber": "+9715XXXXXXXX" } }
  CAMARA response: { "roaming": true|false, "countryCode": <int>, ... }

Note: `known_device` is NOT a CAMARA signal — device-fingerprint
recognition is the *remittance app's* job, not the network's. CAMARA
supplies the network-side signals (roaming, reachability); the app
supplies whether it has seen this device on this account before. In live
mode we take roaming from CAMARA and resolve `known_device` from a local
lookup (KNOWN_DEVICES), which a real deployment would back with its own
device table.

Without NAC_API_KEY (or if the live call fails) everything falls back to
the scenario-keyed mock below — see backend/camara_apis/_nac.py.
"""
from ._nac import NacError, live_enabled, nac_post

# Device fingerprints the app has previously seen on a legitimate session.
# A real deployment reads this from its own datastore per account.
KNOWN_DEVICES = {"device-fp-known-abc123"}

SCENARIOS = {
    "clean": {
        "connectivity_status": "CONNECTED_DATA",
        "roaming": False,
        "known_device": True,
    },
    "sim_swap_block": {
        "connectivity_status": "CONNECTED_DATA",
        "roaming": False,
        "known_device": False,  # new SIM, unrecognized device fingerprint
    },
    "mismatch_stepup": {
        "connectivity_status": "CONNECTED_DATA",
        "roaming": True,
        "known_device": False,
    },
}


class DeviceStatusClient:
    """CAMARA Device Status client."""

    def check(self, phone_number: str, device_fingerprint: str, scenario: str = "clean") -> dict:
        if live_enabled():
            try:
                return self._live(phone_number, device_fingerprint)
            except NacError as exc:
                return self._mock(phone_number, device_fingerprint, scenario,
                                  source="mock-fallback", live_error=str(exc))
        return self._mock(phone_number, device_fingerprint, scenario, source="mock")

    def _live(self, phone_number: str, device_fingerprint: str) -> dict:
        data = nac_post(
            "/camara/device-status/v0/roaming",
            {"device": {"phoneNumber": phone_number}},
        )
        return {
            "api": "device_status",
            "phone_number": phone_number,
            "device_fingerprint": device_fingerprint,
            "connectivity_status": data.get("connectivityStatus", "UNKNOWN"),
            "roaming": bool(data.get("roaming")),
            "known_device": device_fingerprint in KNOWN_DEVICES,
            "source": "live",
        }

    def _mock(self, phone_number: str, device_fingerprint: str, scenario: str,
              *, source: str, live_error: str | None = None) -> dict:
        data = SCENARIOS.get(scenario, SCENARIOS["clean"])
        result = {
            "api": "device_status",
            "phone_number": phone_number,
            "device_fingerprint": device_fingerprint,
            "connectivity_status": data["connectivity_status"],
            "roaming": data["roaming"],
            "known_device": data["known_device"],
            "source": source,
        }
        if live_error:
            result["live_error"] = live_error
        return result
