"""
Force the CAMARA clients into mock mode for the whole test session, so
tests are deterministic even when a real NAC_API_KEY is present in .env.

Live integration is exercised separately by test_live_camara.py, which is
skipped unless RUN_LIVE_CAMARA=1.
"""
import pytest

from backend import config


@pytest.fixture(autouse=True)
def _force_mock_camara(monkeypatch):
    monkeypatch.setattr(config, "USE_LIVE_CAMARA", False)
