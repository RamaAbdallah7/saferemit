"""
CAMARA Device Status API client (live-or-mock).

Live: networkAsCode SDK
     client.device_status.check_roaming(device={"phone_number": ...})
       -> { "roaming": bool, "countryCode": int, "countryName": [str] }
     client.device_status.check_connectivity(device={"phone_number": ...})
       -> { "connectivityStatus": "CONNECTED_DATA"|"CONNECTED_SMS"|"NOT_CONNECTED" }

`known_device` is NOT a CAMARA signal - device-fingerprint recognition is
the remittance app's job, not the network's. CAMARA gives us roaming +
reachability; the app supplies whether it has seen this device on this
account before (resolved here from KNOWN_DEVICES, which a real deployment
backs with its own device table).

Without NAC_API_KEY (or if a live call fails) everything falls back to the
scenario-keyed mock below.
"""
from ._nac import NacError, as_dict, call, client, live_enabled

# Device fingerprints the app has previously seen on a legitimate session.
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
        device = {"phone_number": phone_number}
        roaming = as_dict(call(lambda: client().device_status.check_roaming(device=device)))
        try:
            conn = as_dict(call(lambda: client().device_status.check_connectivity(device=device)))
            conn_status = conn.get("connectivity_status") or conn.get("connectivityStatus") or "UNKNOWN"
        except NacError:
            conn_status = "UNKNOWN"  # connectivity is a nice-to-have; roaming is the signal we score
        return {
            "api": "device_status",
            "phone_number": phone_number,
            "device_fingerprint": device_fingerprint,
            "connectivity_status": conn_status,
            "roaming": bool(roaming.get("roaming")),
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
