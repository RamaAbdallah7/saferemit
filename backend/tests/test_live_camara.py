"""
Opt-in live integration test against the Nokia Network-as-Code simulated
network. Skipped unless RUN_LIVE_CAMARA=1 and NAC_API_KEY is set.

    RUN_LIVE_CAMARA=1 python -m pytest backend/tests/test_live_camara.py -v

Uses the NaC API Playground simulator MSISDN. Each client falls back to
mock on failure, so this test asserts on the `source` field to prove the
call actually reached the live API.
"""
import os

import pytest

from backend import config

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_LIVE_CAMARA") != "1" or not config.NAC_API_KEY,
    reason="set RUN_LIVE_CAMARA=1 and NAC_API_KEY to run live integration tests",
)

SIMULATOR_NUMBER = os.environ.get("NAC_SIM_NUMBER", "+99999991000")


@pytest.fixture(autouse=True)
def _force_live_camara(monkeypatch):
    monkeypatch.setattr(config, "USE_LIVE_CAMARA", True)


def test_sim_swap_live():
    from backend.camara_apis.sim_swap import SimSwapClient

    result = SimSwapClient().check(SIMULATOR_NUMBER, max_age_hours=240)
    assert result["source"] == "live", result.get("live_error")
    assert isinstance(result["swapped"], bool)


def test_device_status_live():
    from backend.camara_apis.device_status import DeviceStatusClient

    result = DeviceStatusClient().check(SIMULATOR_NUMBER, "device-fp-known-abc123")
    assert result["source"] == "live", result.get("live_error")
    assert isinstance(result["roaming"], bool)


def test_location_verification_live():
    from backend.camara_apis.location_verification import LocationVerificationClient

    result = LocationVerificationClient().verify(SIMULATOR_NUMBER, "Dubai, UAE")
    assert result["source"] == "live", result.get("live_error")
    assert result["verification_result"] in {"TRUE", "FALSE", "PARTIAL", "UNKNOWN"}
