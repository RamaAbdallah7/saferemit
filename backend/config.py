"""
Central configuration for the SafeRemit backend.

Every value is read from the environment so nothing secret is ever
committed. Copy `.env.example` to `.env` and fill in what you have — the
app runs fully without any of these set (mock CAMARA data + deterministic
rationale), which is the "cached demo data" fallback the hackathon's
Resource & Tooling Guide recommends.
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    # Load <project-root>/.env if present. Real environment variables always win.
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:  # python-dotenv is optional; env vars still work without it
    pass


def _clean(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


# --- Nokia Network-as-Code / CAMARA -----------------------------------------
# The NaC developer portal fronts the CAMARA APIs through an apihub gateway.
# In Simulator mode a single RapidAPI-style key works across every endpoint;
# the two values below come straight from the portal's Console "cURL" snippet
# (API Playground -> any endpoint -> Code Snippets).
NAC_API_KEY = _clean("NAC_API_KEY")
NAC_BASE_URL = _clean("NAC_BASE_URL", "https://network-as-code.p-eu.apihub.nokia.io").rstrip("/")
NAC_RAPIDAPI_HOST = _clean("NAC_RAPIDAPI_HOST", "network-as-code.nokia.rapidapi.com")
CAMARA_TIMEOUT_SECONDS = float(_clean("CAMARA_TIMEOUT_SECONDS", "10"))

# Live CAMARA calls are attempted only when a key is present. Without it,
# every client returns scenario-keyed mock data instead.
USE_LIVE_CAMARA = bool(NAC_API_KEY)


# --- LLM rationale (Google AI Studio / Gemini) ------------------------------
# Listed in the Resource & Tooling Guide, section 3 ("Hosted APIs with a
# free tier"). Optional — rationale falls back to a deterministic template.
GEMINI_API_KEY = _clean("GEMINI_API_KEY")
GEMINI_MODEL = _clean("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_TIMEOUT_SECONDS = float(_clean("GEMINI_TIMEOUT_SECONDS", "4"))


def status() -> dict:
    """Small non-secret summary, surfaced at GET /api/health so a judge can
    see at a glance whether the demo is running live or on mock data."""
    return {
        "camara_mode": "live" if USE_LIVE_CAMARA else "mock",
        "camara_gateway": NAC_BASE_URL if USE_LIVE_CAMARA else None,
        "rationale_mode": "gemini" if GEMINI_API_KEY else "template",
        "gemini_model": GEMINI_MODEL if GEMINI_API_KEY else None,
    }
