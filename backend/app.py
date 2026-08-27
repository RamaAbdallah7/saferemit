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
        request = preset["request"]
        scenario_key = preset["id"]
    else:
        if not body.phone_number:
            raise HTTPException(status_code=400, detail="phone_number is required when no scenario is given")
        request = body.model_dump(exclude={"scenario"})
        scenario_key = "clean"  # live/manual requests fall back to the "clean" mock signal set

    result = agent.decide(request, scenario=scenario_key)
    return result


# Serve the demo frontend as static files at the root, so `uvicorn backend.app:app`
# is the only thing you need running for the whole demo.
_frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if _frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dir), html=True), name="frontend")
