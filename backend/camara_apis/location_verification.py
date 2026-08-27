"""
Mock for the CAMARA Location Verification API.

Real endpoint (Nokia Network-as-Code):
  POST https://network-as-code.p-eu.rapidapi.com/camara/location-verification/v0/verify
  Body: { "device": { "phoneNumber": "+9715XXXXXXXX" },
          "latitude": 25.276987, "longitude": 55.296249, "accuracy": 5000 }
  Docs: https://developer.networkascode.nokia.io/

Real response shape (CAMARA spec):
  { "verificationResult": "TRUE" | "FALSE" | "PARTIAL", "matchRate": 0-100 }

TODO (swap-in):
    device = client.devices.get(phone_number=phone_number)
    return device.location.verify(latitude=lat, longitude=lon, radius=accuracy_m)
"""

SCENARIOS = {
    "clean": {"verification_result": "TRUE", "match_rate": 97},
    "sim_swap_block": {"verification_result": "PARTIAL", "match_rate": 54},
    "mismatch_stepup": {"verification_result": "FALSE", "match_rate": 12},
}


class LocationVerificationClient:
    """Mock CAMARA Location Verification client."""

    def verify(self, phone_number: str, claimed_location: str, scenario: str = "clean") -> dict:
        data = SCENARIOS.get(scenario, SCENARIOS["clean"])
        return {
            "api": "location_verification",
            "phone_number": phone_number,
            "claimed_location": claimed_location,
            "verification_result": data["verification_result"],
            "match_rate": data["match_rate"],
        }
