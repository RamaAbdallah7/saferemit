"""
Force deterministic mode for the whole test session, so tests pass the
same way whether or not real keys are present in .env:

  * CAMARA clients -> mock data (no live calls)
  * LLM analyst    -> off (no Gemini calls)

The live paths are exercised separately by test_live_camara.py, which is
skipped unless RUN_LIVE_CAMARA=1.
"""
import pytest

from backend import config


@pytest.fixture(autouse=True)
def _force_deterministic(monkeypatch):
    monkeypatch.setattr(config, "USE_LIVE_CAMARA", False)
    monkeypatch.setattr(config, "USE_LLM_ASSESSMENT", False)
