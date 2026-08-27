"""
Shared plumbing for the four CAMARA API clients.

Each client is "live-or-mock":

  * If NAC_API_KEY is set, it calls the real Nokia Network-as-Code
    endpoint (CAMARA-standard request/response shapes).
  * If the key is absent, OR the live call errors / times out, it returns
    scenario-keyed mock data instead and marks the signal `source`
    accordingly.

That graceful degradation is exactly what the hackathon's Resource &
Tooling Guide tells participants to build: "Have a clear fallback when an
API or model is rate-limited" and "Cache demo data. Live API calls fail
at the worst moment."

NaC portal specifics (verify against your portal's "Endpoints" tab once
you have a key — RapidAPI hubs occasionally version the path prefix):
  Base:    https://network-as-code.p-eu.rapidapi.com
  Headers: x-rapidapi-key, x-rapidapi-host
"""
from __future__ import annotations

import requests

from .. import config


class NacError(RuntimeError):
    """Raised when a live Network-as-Code call fails; callers catch this
    and fall back to mock data."""


def live_enabled() -> bool:
    return config.USE_LIVE_CAMARA


def nac_post(path: str, payload: dict) -> dict:
    """POST to a Network-as-Code CAMARA endpoint and return parsed JSON.

    Raises NacError on any transport/HTTP/parse failure so every client
    can use one `except NacError` fallback path.
    """
    url = f"{config.NAC_BASE_URL}{path}"
    headers = {
        "x-rapidapi-key": config.NAC_API_KEY,
        "x-rapidapi-host": config.NAC_API_HOST,
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(
            url, json=payload, headers=headers, timeout=config.CAMARA_TIMEOUT_SECONDS
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:  # network, timeout, non-2xx
        raise NacError(f"{path} -> {exc}") from exc
    except ValueError as exc:  # non-JSON body
        raise NacError(f"{path} -> invalid JSON response") from exc
