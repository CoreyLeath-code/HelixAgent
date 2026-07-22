# api/main.py

"""
HelixAgent FastAPI Application
-------------------------------
Main API entrypoint. Mounts monitoring (Prometheus + OpenTelemetry) and
exposes core routes for agent inference.
"""

import os

from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from agent.autonomy.models import AgentRun
from agent.autonomy.runtime import AutonomousRuntime
from agent.autonomy.store import RunNotFoundError
from api.monitoring import setup_monitoring

app = FastAPI(
    title="HelixAgent API",
    description="Modular AI agent framework for automation, reasoning, and decision-making.",
    version="1.0.0",
)

# Attach Prometheus metrics + OpenTelemetry tracing
setup_monitoring(app)


class PredictRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4_000)


class RunRequest(BaseModel):
    objective: str = Field(min_length=1, max_length=4_000)
    max_iterations: int = Field(default=12, ge=1, le=100)
    tool_budget: int = Field(default=10, ge=1, le=100)


class ApprovalDecision(BaseModel):
    approved: bool


runtime = AutonomousRuntime()


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to health check."""
    return JSONResponse({"status": "ok", "service": "HelixAgent"})


@app.get("/health", tags=["Operations"])
async def health():
    """Liveness / readiness probe for container orchestration."""
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/predict", tags=["Agent"])
async def predict(payload: PredictRequest):
    """Backward-compatible synchronous endpoint."""
    run = runtime.submit(payload.prompt)
    completed = runtime.run(run.id)
    if completed.error:
        raise HTTPException(status_code=503, detail={"run_id": run.id, "error": completed.error})
    return {"run_id": run.id, "status": completed.status, "result": completed.final_output}


@app.post("/runs", response_model=AgentRun, status_code=status.HTTP_202_ACCEPTED, tags=["Agent"])
async def create_run(payload: RunRequest, background_tasks: BackgroundTasks) -> AgentRun:
    """Create a durable autonomous run and execute it outside the request lifecycle."""
    run = runtime.submit(
        payload.objective,
        max_iterations=payload.max_iterations,
        tool_budget=payload.tool_budget,
    )
    background_tasks.add_task(runtime.run, run.id)
    return run


@app.get("/runs/{run_id}", response_model=AgentRun, tags=["Agent"])
async def get_run(run_id: str) -> AgentRun:
    try:
        return runtime.store.get(run_id)
    except RunNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc


@app.post("/runs/{run_id}/approvals/{task_id}", response_model=AgentRun, tags=["Agent"])
async def decide_approval(
    run_id: str,
    task_id: str,
    payload: ApprovalDecision,
    background_tasks: BackgroundTasks,
) -> AgentRun:
    try:
        run = runtime.approve(run_id, task_id, payload.approved)
    except (RunNotFoundError, KeyError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if payload.approved:
        background_tasks.add_task(runtime.run, run.id)
    return run


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run("api.main:app", host=host, port=port, reload=False)
