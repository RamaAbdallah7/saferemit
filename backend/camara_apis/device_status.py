"""
Mock for the CAMARA Device Status API (reachability + roaming status).

Real endpoint (Nokia Network-as-Code):
  POST https://network-as-code.p-eu.rapidapi.com/camara/device-status/v0/connectivity
  Body: { "device": { "phoneNumber": "+9715XXXXXXXX" } }
  Docs: https://developer.networkascode.nokia.io/

Real response shape (CAMARA spec):
  { "connectivityStatus": "CONNECTED_SMS" | "CONNECTED_DATA" | "NOT_CONNECTED",
    "roaming": true|false }

TODO (swap-in):
    device = client.devices.get(phone_number=phone_number)
    return device.status.connectivity(), device.status.roaming()
"""

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
    """Mock CAMARA Device Status client."""

    def check(self, phone_number: str, device_fingerprint: str, scenario: str = "clean") -> dict:
        data = SCENARIOS.get(scenario, SCENARIOS["clean"])
        return {
            "api": "device_status",
            "phone_number": phone_number,
            "device_fingerprint": device_fingerprint,
            "connectivity_status": data["connectivity_status"],
            "roaming": data["roaming"],
            "known_device": data["known_device"],
        }
