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


# Serve the built React frontend at the root, so `uvicorn backend.app:app`
# alone runs the whole demo (after `npm run build` in frontend/).
#
# While iterating on the UI, run `npm run dev` in frontend/ instead — the
# Vite dev server on :5173 proxies /api to this backend on :8000, so
# App.jsx's fetch("/api/...") works the same in dev and in the build.
_react_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if _react_dist.exists():
    app.mount("/", StaticFiles(directory=str(_react_dist), html=True), name="frontend")
else:
    @app.get("/", include_in_schema=False)
    def _needs_build():
        return {"detail": "Frontend not built. Run `npm run build` in frontend/, then reload."}
