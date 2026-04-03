from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environment import EmailTriageEnvironment
from tasks import TASKS

app = FastAPI(
    title="Email Triage Environment",
    description="An OpenEnv environment for email triage and response tasks",
    version="1.0.0"
)

env = EmailTriageEnvironment()

class ResetRequest(BaseModel):
    task_name: Optional[str] = "task_1_easy"

class StepRequest(BaseModel):
    action: dict

@app.get("/")
def root():
    return {
        "status": "ok",
        "environment": "Email Triage Environment",
        "version": "1.0.0",
        "tasks": ["task_1_easy", "task_2_medium", "task_3_hard"]
    }

@app.post("/reset")
def reset(request: ResetRequest):
    valid_tasks = ["task_1_easy", "task_2_medium", "task_3_hard"]
    if request.task_name not in valid_tasks:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid task. Choose from: {valid_tasks}"
        )
    observation = env.reset(request.task_name)
    return {"observation": observation, "status": "episode started"}

@app.post("/step")
def step(request: StepRequest):
    if env.current_email is None:
        raise HTTPException(
            status_code=400,
            detail="Environment not started. Call /reset first."
        )
    return env.step(request.action)

@app.get("/state")
def state():
    return env.state()

@app.get("/tasks")
def list_tasks():
    return {
        task_name: {
            "name": task["name"],
            "description": task["description"],
            "difficulty": task["difficulty"],
            "num_emails": len(task["emails"])
        }
        for task_name, task in TASKS.items()
    }

def main():
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=7860,
        reload=False
    )

if __name__ == "__main__":
    main()
