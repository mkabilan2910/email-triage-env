# server.py — FastAPI web server that wraps our environment

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

from environment import EmailTriageEnvironment

# Create the FastAPI app
app = FastAPI(
    title="Email Triage Environment",
    description="An OpenEnv environment for email triage and response tasks",
    version="1.0.0"
)

# Create one environment instance
env = EmailTriageEnvironment()


# ── Request models ──────────────────────────────────────────
class ResetRequest(BaseModel):
    task_name: Optional[str] = "task_1_easy"


class StepRequest(BaseModel):
    action: dict


# ── Endpoints ───────────────────────────────────────────────

@app.get("/")
def root():
    """Health check — judges ping this to confirm server is alive"""
    return {
        "status": "ok",
        "environment": "Email Triage Environment",
        "version": "1.0.0",
        "tasks": ["task_1_easy", "task_2_medium", "task_3_hard"]
    }


@app.post("/reset")
def reset(request: ResetRequest):
    """Start a fresh episode. Returns first observation."""
    valid_tasks = ["task_1_easy", "task_2_medium", "task_3_hard"]

    if request.task_name not in valid_tasks:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid task. Choose from: {valid_tasks}"
        )

    observation = env.reset(request.task_name)
    return {
        "observation": observation,
        "status": "episode started"
    }


@app.post("/step")
def step(request: StepRequest):
    """Agent submits an action. Returns observation, reward, done, info."""
    if env.current_email is None:
        raise HTTPException(
            status_code=400,
            detail="Environment not started. Call /reset first."
        )

    result = env.step(request.action)
    return result


@app.get("/state")
def state():
    """Returns current state of the environment."""
    return env.state()


@app.get("/tasks")
def list_tasks():
    """Lists all available tasks with descriptions."""
    from tasks import TASKS
    return {
        task_name: {
            "name": task["name"],
            "description": task["description"],
            "difficulty": task["difficulty"],
            "num_emails": len(task["emails"])
        }
        for task_name, task in TASKS.items()
    }


# ── Run the server ───────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=7860,
        reload=True
    )