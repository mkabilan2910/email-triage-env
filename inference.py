# inference.py — Baseline agent that runs against our environment
# Uses OpenAI client as required by the hackathon rules

import os
import json
import requests
from openai import OpenAI

# ── Configuration ────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY")
MODEL_NAME   = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
SERVER_URL   = os.getenv("SERVER_URL", "http://localhost:8000")

# ── OpenAI Client ────────────────────────────────────────────
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY if API_KEY else "dummy-key-for-local-testing"
)

# ── Prompts for each task ────────────────────────────────────
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
{{"reply": "Dear Customer, we apologize for the inconvenience..."}}

Your reply must:
- Start with an apology
- Address the specific issue
- Provide clear next steps
- Be professional and empathetic

Email Subject: {subject}
Email Body: {body}

Respond with JSON only. No explanation."""
}


# ── Helper functions ─────────────────────────────────────────
def call_reset(task_name: str) -> dict:
    """Call /reset endpoint to start a fresh episode"""
    response = requests.post(
        f"{SERVER_URL}/reset",
        json={"task_name": task_name}
    )
    return response.json()


def call_step(action: dict) -> dict:
    """Call /step endpoint to submit an action"""
    response = requests.post(
        f"{SERVER_URL}/step",
        json={"action": action}
    )
    return response.json()


def call_state() -> dict:
    """Call /state endpoint to get current state"""
    response = requests.get(f"{SERVER_URL}/state")
    return response.json()


def ask_llm(task_name: str, subject: str, body: str) -> dict:
    """Send email to LLM and get structured response"""
    prompt = TASK_PROMPTS[task_name].format(
        subject=subject,
        body=body
    )

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that responds only in JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.0,
            max_tokens=300
        )

        response_text = completion.choices[0].message.content.strip()

        # Clean up response — remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        return json.loads(response_text)

    except Exception as e:
        print(f"  LLM call failed: {e}")
        print("  Using fallback answer...")
        # Fallback answers if LLM fails
        fallbacks = {
            "task_1_easy":   {"category": "general", "priority": "low"},
            "task_2_medium": {"name": "unknown", "issue": "unknown", "urgency": "low"},
            "task_3_hard":   {"reply": "We apologize for the inconvenience. Our team will contact you within 3 days with next steps."}
        }
        return fallbacks[task_name]


def run_task(task_name: str, num_episodes: int = 3) -> float:
    """
    Run multiple episodes of a task and return average reward.
    num_episodes=3 means we test all 3 emails in the task.
    """
    print(f"\n{'='*50}")
    print(f"Running {task_name}")
    print(f"{'='*50}")

    total_reward = 0.0

    for episode in range(num_episodes):
        print(f"\n  Episode {episode + 1}/{num_episodes}")

        # Reset environment
        reset_response = call_reset(task_name)
        observation = reset_response["observation"]

        subject = observation["email"]["subject"]
        body    = observation["email"]["body"]

        print(f"  Email: {subject}")

        # Ask LLM for answer
        action = ask_llm(task_name, subject, body)
        print(f"  Action: {action}")

        # Submit answer
        result = call_step(action)
        reward = result.get("reward", 0.0)
        total_reward += reward

        print(f"  Reward: {reward}")

    avg_reward = round(total_reward / num_episodes, 3)
    print(f"\n  Average reward for {task_name}: {avg_reward}")
    return avg_reward


# ── Main ─────────────────────────────────────────────────────
def main():
    print("=" * 50)
    print("Email Triage Environment — Baseline Agent")
    print("=" * 50)
    print(f"Server  : {SERVER_URL}")
    print(f"Model   : {MODEL_NAME}")

    # Check server is running
    try:
        response = requests.get(f"{SERVER_URL}/")
        print(f"Server status: {response.json()['status']}")
    except Exception:
        print("ERROR: Server is not running!")
        print(f"Please start it with: uvicorn server:app --host 0.0.0.0 --port 8000")
        return

    # Run all 3 tasks
    scores = {}
    scores["task_1_easy"]   = run_task("task_1_easy",   num_episodes=3)
    scores["task_2_medium"] = run_task("task_2_medium", num_episodes=3)
    scores["task_3_hard"]   = run_task("task_3_hard",   num_episodes=3)

    # Print final summary
    print(f"\n{'='*50}")
    print("BASELINE SCORES SUMMARY")
    print(f"{'='*50}")
    for task, score in scores.items():
        bar = "█" * int(score * 20)
        print(f"  {task:20s} : {score:.3f}  {bar}")

    overall = round(sum(scores.values()) / len(scores), 3)
    print(f"\n  Overall average score : {overall}")
    print(f"{'='*50}")
    print("\nBaseline run complete!")


if __name__ == "__main__":
    main()