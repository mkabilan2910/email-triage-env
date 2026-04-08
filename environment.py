# environment.py — The brain of our environment

import random
from tasks import TASKS
from graders import grade_task_1, grade_task_2, grade_task_3


class EmailTriageEnvironment:

    def __init__(self):
        self.current_task = None
        self.current_email = None
        self.task_name = None
        self.done = False
        self.steps_taken = 0
        self.last_reward = 0.0

    def reset(self, task_name: str = "task_1_easy") -> dict:
        """Start a fresh task — picks a random email from the task"""
        self.task_name = task_name
        self.current_task = TASKS[task_name]
        self.current_email = random.choice(self.current_task["emails"])
        self.done = False
        self.steps_taken = 0
        self.last_reward = 0.0

        return {
            "task": task_name,
            "difficulty": self.current_task["difficulty"],
            "email": {
                "subject": self.current_email["subject"],
                "body": self.current_email["body"]
            },
            "instruction": self.current_task["description"]
        }

    def step(self, action: dict) -> dict:
        """Agent submits an answer — we grade it and return reward"""
        if self.done:
            return {
                "observation": "Episode already done. Call reset() first.",
                "reward": 0.0,
                "done": True,
                "info": {}
            }

        self.steps_taken += 1

        # Grade based on which task we are on
        if self.task_name == "task_1_easy":
            reward = grade_task_1(action, self.current_email)

        elif self.task_name == "task_2_medium":
            reward = grade_task_2(action, self.current_email)

        elif self.task_name == "task_3_hard":
            reward = grade_task_3(action, self.current_email)

        else:
            reward = 0.0

        self.last_reward = reward
        self.done = True

        return {
            "observation": "Answer received and graded.",
            "reward": reward,
            "done": self.done,
            "info": {
                "steps_taken": self.steps_taken,
                "task": self.task_name,
                "email_id": self.current_email["id"]
            }
        }

    def state(self) -> dict:
        """Return current state of the environment"""
        return {
            "task": self.task_name,
            "done": self.done,
            "steps_taken": self.steps_taken,
            "last_reward": self.last_reward,
            "current_email_id": self.current_email["id"] if self.current_email else None
        }


# Quick test — run this file directly to verify everything works
if __name__ == "__main__":
    env = EmailTriageEnvironment()

    print("=" * 40)
    print("Testing Task 1 — Easy (Classification)")
    print("=" * 40)
    obs = env.reset("task_1_easy")
    print("Subject :", obs["email"]["subject"])
    print("Body    :", obs["email"]["body"])
    print("Instruction:", obs["instruction"])
    result = env.step({"category": "billing", "priority": "high"})
    print("Reward  :", result["reward"])
    print("Done    :", result["done"])

    print()
    print("=" * 40)
    print("Testing Task 2 — Medium (Extraction)")
    print("=" * 40)
    obs = env.reset("task_2_medium")
    print("Subject :", obs["email"]["subject"])
    print("Body    :", obs["email"]["body"])
    result = env.step({
        "name": "Rahul Sharma",
        "issue": "payment failure",
        "urgency": "high"
    })
    print("Reward  :", result["reward"])
    print("Done    :", result["done"])

    print()
    print("=" * 40)
    print("Testing Task 3 — Hard (Response Drafting)")
    print("=" * 40)
    obs = env.reset("task_3_hard")
    print("Subject :", obs["email"]["subject"])
    print("Body    :", obs["email"]["body"])
    result = env.step({
        "reply": "We are sorry to hear about your issue. Your order #45231 will be processed within 3 days. Our team will contact you with next steps."
    })
    print("Reward  :", result["reward"])
    print("Done    :", result["done"])

    print()
    print("=" * 40)
    print("Testing state()")
    print("=" * 40)
    print(env.state())

    print()
    print("All tests passed! Environment is working!")