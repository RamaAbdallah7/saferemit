"""
Shared plumbing for the four CAMARA API clients.

Each client is "live-or-mock":

  * If NAC_API_KEY is set, it POSTs to the real Nokia Network-as-Code
    apihub gateway (CAMARA-standard request/response bodies).
  * If the key is absent, OR the live call errors / times out, it returns
    scenario-keyed mock data instead and marks the signal `source`
    accordingly ("mock" / "mock-fallback").

That graceful degradation is exactly what the hackathon's Resource &
Tooling Guide tells participants to build: "Have a clear fallback when an
API or model is rate-limited" and "Cache demo data. Live API calls fail
at the worst moment."

Endpoints + headers below are taken verbatim from the portal Console's
cURL snippets (API Playground -> endpoint -> Code Snippets), Simulator
mode. Test with the simulator MSISDN +99999991000, not a real SIM.
"""
from __future__ import annotations

import requests

from .. import config


class NacError(RuntimeError):
    """Raised when a live Network-as-Code call fails; every client catches
    this and falls back to mock data."""


def live_enabled() -> bool:
    return config.USE_LIVE_CAMARA


def nac_post(path: str, payload: dict) -> dict:
    """POST to a Network-as-Code CAMARA endpoint and return parsed JSON.

    Raises NacError on any transport/HTTP/parse failure so every client
    can use one `except NacError` fallback path.
    """
    url = f"{config.NAC_BASE_URL}/{path.lstrip('/')}"
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": config.NAC_RAPIDAPI_HOST,
        "x-rapidapi-key": config.NAC_API_KEY,
    }
    try:
        resp = requests.post(
            url, json=payload, headers=headers, timeout=config.CAMARA_TIMEOUT_SECONDS
        )
        resp.raise_for_status()
        return resp.json() if resp.content else {}
    except requests.HTTPError as exc:
        body = exc.response.text[:300] if exc.response is not None else ""
        raise NacError(f"{path} -> HTTP {exc.response.status_code if exc.response else '?'}: {body}") from exc
    except requests.RequestException as exc:  # network, timeout
        raise NacError(f"{path} -> {exc}") from exc
    except ValueError as exc:  # non-JSON body
        raise NacError(f"{path} -> invalid JSON response") from exc
