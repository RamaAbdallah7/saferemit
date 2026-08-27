"""
Mock for the CAMARA Number Verification API.

Real endpoint (Nokia Network-as-Code):
  POST https://network-as-code.p-eu.rapidapi.com/camara/number-verification/v0/verify
  Body: { "phoneNumber": "+9715XXXXXXXX" }
  Docs: https://developer.networkascode.nokia.io/

Real response shape (CAMARA spec):
  { "devicePhoneNumberVerified": true|false }

TODO (swap-in):
    device = client.devices.get(phone_number=phone_number)
    return device.number_verification.verify()
"""

SCENARIOS = {
    "clean": {"verified": True},
    "sim_swap_block": {"verified": True},   # number itself checks out; SIM swap is the red flag
    "mismatch_stepup": {"verified": True},
}


class NumberVerificationClient:
    """Mock CAMARA Number Verification client."""

    def verify(self, phone_number: str, scenario: str = "clean") -> dict:
        data = SCENARIOS.get(scenario, SCENARIOS["clean"])
        return {
            "api": "number_verification",
            "phone_number": phone_number,
            "verified": data["verified"],
        }
