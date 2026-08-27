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
# The NaC developer portal is a white-labelled RapidAPI hub; a single
# x-rapidapi-key works across every API you've subscribed to.
NAC_API_KEY = _clean("NAC_API_KEY")
NAC_API_HOST = _clean("NAC_API_HOST", "network-as-code.p-eu.rapidapi.com")
NAC_BASE_URL = f"https://{NAC_API_HOST}"
CAMARA_TIMEOUT_SECONDS = float(_clean("CAMARA_TIMEOUT_SECONDS", "6"))

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
        "camara_host": NAC_API_HOST if USE_LIVE_CAMARA else None,
        "rationale_mode": "gemini" if GEMINI_API_KEY else "template",
        "gemini_model": GEMINI_MODEL if GEMINI_API_KEY else None,
    }
