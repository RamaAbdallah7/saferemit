"""
Shared plumbing for the four CAMARA API clients.

Each client is "live-or-mock":

  * If NAC_API_KEY is set, it calls the real Nokia Network-as-Code API
    through the official `networkAsCode` SDK.
  * If the key is absent, OR the live call errors / times out, it returns
    scenario-keyed mock data instead and marks the signal `source`
    accordingly ("mock" / "mock-fallback").

That graceful degradation is exactly what the hackathon's Resource &
Tooling Guide tells participants to build: "Have a clear fallback when an
API or model is rate-limited" and "Cache demo data. Live API calls fail
at the worst moment."

Setup:
    pip install networkAsCode
    # in .env:  NAC_API_KEY=<x-rapidapi-key from networkascode.nokia.io>

Test numbers: the NaC API Playground runs a simulated network — use its
documented simulator MSISDNs (e.g. +99999991000) rather than real SIMs.
"""
from __future__ import annotations

import functools

from .. import config


class NacError(RuntimeError):
    """Raised when a live Network-as-Code call fails; every client catches
    this and falls back to mock data."""


def live_enabled() -> bool:
    return config.USE_LIVE_CAMARA


@functools.lru_cache(maxsize=1)
def client():
    """Lazily build one shared SDK client. Cached so we don't re-create an
    httpx pool per call. Raises NacError if the SDK isn't installed."""
    try:
        from network_as_code import NetworkAsCodeApi  # type: ignore
    except ImportError as exc:  # pragma: no cover - depends on install
        raise NacError(
            "networkAsCode SDK not installed - run `pip install networkAsCode`"
        ) from exc
    return NetworkAsCodeApi(
        rapidapi_host=config.NAC_API_HOST,
        api_key=config.NAC_API_KEY,
        timeout=config.CAMARA_TIMEOUT_SECONDS,
    )


def call(fn):
    """Run an SDK call, normalising every failure into NacError so each
    client can use one `except NacError` fallback path."""
    try:
        return fn()
    except NacError:
        raise
    except Exception as exc:  # SDK ApiError, httpx errors, parse errors, ...
        raise NacError(f"{type(exc).__name__}: {exc}") from exc


def as_dict(model) -> dict:
    """Best-effort dict from a pydantic SDK response (v1 or v2)."""
    for attr in ("model_dump", "dict"):
        if hasattr(model, attr):
            try:
                return getattr(model, attr)()
            except Exception:  # pragma: no cover
                pass
    return dict(getattr(model, "__dict__", {}))
