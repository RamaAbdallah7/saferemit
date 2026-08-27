"""
SafeRemit API — run with:
    uvicorn backend.app:app --reload --app-dir <project-root>

or, from the project root:
    python -m uvicorn backend.app:app --reload
"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config
from .agent.orchestrator import SafeRemitAgent
from .scenarios import list_scenarios, get_scenario

app = FastAPI(title="SafeRemit", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = SafeRemitAgent()


class DecideRequest(BaseModel):
    scenario: str | None = None
    phone_number: str | None = None
    action_type: str | None = "login"
    device_fingerprint: str | None = None
    claimed_location: str | None = None


@app.get("/api/health")
def api_health():
    """Non-secret runtime summary — lets a judge see at a glance whether
    the demo is running on live CAMARA calls or mock data."""
    return {"status": "ok", **config.status()}


@app.get("/api/scenarios")
def api_list_scenarios():
    return {"scenarios": list_scenarios()}


@app.post("/api/decide")
def api_decide(body: DecideRequest):
    if body.scenario:
        try:
            preset = get_scenario(body.scenario)
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e))
        request = dict(preset["request"])
        scenario_key = preset["id"]
        # In live mode, run the scenario against its real simulator MSISDN
        # so the CAMARA calls are genuine while still telling the scripted
        # story. Scenarios without a live_phone stay on mock data.
        if config.USE_LIVE_CAMARA and preset.get("live_phone"):
            request["phone_number"] = preset["live_phone"]
    else:
        if not body.phone_number:
            raise HTTPException(status_code=400, detail="phone_number is required when no scenario is given")
        request = body.model_dump(exclude={"scenario"})
        scenario_key = "clean"  # live/manual requests fall back to the "clean" mock signal set

    result = agent.decide(request, scenario=scenario_key)
    return result


# Serve the built React frontend as static files at the root, so
# `uvicorn backend.app:app` alone can run the whole demo (after `npm run
# build` in frontend/ — see frontend/README or PROTOTYPE_NOTES.md).
#
# While actively developing the UI, run `npm run dev` in frontend/ instead
# (Vite dev server on :5173, proxying /api to this backend on :8000) — much
# faster iteration than rebuilding on every change.
_project_root = Path(__file__).resolve().parent.parent
_react_dist = _project_root / "frontend" / "dist"
_vanilla_frontend = _project_root / "frontend-vanilla"

if _react_dist.exists():
    app.mount("/", StaticFiles(directory=str(_react_dist), html=True), name="frontend")
elif _vanilla_frontend.exists():
    # Fallback so `uvicorn backend.app:app` still serves *something* before
    # you've run `npm install && npm run build` in frontend/.
    app.mount("/", StaticFiles(directory=str(_vanilla_frontend), html=True), name="frontend-vanilla")
