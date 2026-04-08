import os
import json
import requests
from openai import OpenAI
from typing import List, Optional

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/groq/openai/v1")
API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
MODEL_NAME   = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
SERVER_URL   = os.getenv("SERVER_URL", "http://localhost:7860")
BENCHMARK    = "email-triage-env"

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY if API_KEY else "dummy-key"
)

TASK_PROMPTS = {
    "task_1_easy": """You are an email classification agent.
Read the email below and classify it.
Respond with ONLY a JSON object like this:
{{"category": "billing", "priority": "high"}}
Category must be exactly one of: billing, technical, general, complaint
Priority must be exactly one of: low, medium, high
Email Subject: {subject}
Email Body: {body}
Respond with JSON only. No explanation.""",

    "task_2_medium": """You are an email information extraction agent.
Read the email below and extract key information.
Respond with ONLY a JSON object like this:
{{"name": "John Smith", "issue": "payment failure", "urgency": "high"}}
Urgency must be exactly one of: low, medium, high
Email Subject: {subject}
Email Body: {body}
Respond with JSON only. No explanation.""",

    "task_3_hard": """You are a professional customer support agent.
Read the email below and write a professional reply.
Respond with ONLY a JSON object like this:
{{"reply": "Dear Customer, we apologize..."}}
Your reply must start with an apology, address the issue, and provide next steps.
Email Subject: {subject}
Email Body: {body}
Respond with JSON only. No explanation."""
}


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def call_reset(task_name: str) -> dict:
    response = requests.post(f"{SERVER_URL}/reset", json={"task_name": task_name})
    return response.json()


def call_step(action: dict) -> dict:
    response = requests.post(f"{SERVER_URL}/step", json={"action": action})
    return response.json()


def ask_llm(task_name: str, subject: str, body: str) -> dict:
    prompt = TASK_PROMPTS[task_name].format(subject=subject, body=body)
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that responds only in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=300
        )
        response_text = completion.choices[0].message.content.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        return json.loads(response_text)
    except Exception as e:
        fallbacks = {
            "task_1_easy":   {"category": "general", "priority": "low"},
            "task_2_medium": {"name": "unknown", "issue": "unknown", "urgency": "low"},
            "task_3_hard":   {"reply": "We apologize for the inconvenience. Our team will contact you within 3 days with next steps."}
        }
        return fallbacks[task_name]


def run_task(task_name: str) -> None:
    rewards = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    try:
        for step in range(1, 4):
            reset_response = call_reset(task_name)
            observation = reset_response["observation"]
            subject = observation["email"]["subject"]
            body = observation["email"]["body"]

            action = ask_llm(task_name, subject, body)
            action_str = json.dumps(action).replace(" ", "")

            result = call_step(action)
            reward = result.get("reward", 0.0)
            done = result.get("done", True)

            rewards.append(reward)
            steps_taken = step

            log_step(step=step, action=action_str, reward=reward, done=done, error=None)

        score = sum(rewards) / len(rewards) if rewards else 0.0
        score = min(max(score, 0.0), 1.0)
        success = score >= 0.1

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


def main():
    try:
        response = requests.get(f"{SERVER_URL}/")
        response.json()
    except Exception:
        print(f"ERROR: Server not running at {SERVER_URL}")
        return

    run_task("task_1_easy")
    run_task("task_2_medium")
    run_task("task_3_hard")


if __name__ == "__main__":
    main()