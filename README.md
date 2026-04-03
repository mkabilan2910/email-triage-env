---
title: Email Triage Environment
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
tags:
  - openenv
---

# 📧 Email Triage Environment

A real-world **OpenEnv** environment where AI agents must triage and respond to customer support emails — a task performed millions of times daily by support teams worldwide.

## 🌍 Real-World Utility

Email triage is one of the most common workflows in any business. This environment tests whether an AI agent can:
- Understand email context and intent
- Extract structured information from unstructured text
- Generate professional, empathetic responses

## 🎯 Tasks

| Task | Name | Difficulty | Description |
|------|------|-----------|-------------|
| task_1_easy | Email Classification | Easy | Classify email into category and priority |
| task_2_medium | Email Info Extraction | Medium | Extract name, issue type and urgency |
| task_3_hard | Email Response Drafting | Hard | Draft a full professional reply |

## 📊 Baseline Scores

Baseline agent: `llama-3.3-70b-versatile` via Groq

| Task | Difficulty | Baseline Score |
|------|-----------|---------------|
| task_1_easy | Easy | 1.000 |
| task_2_medium | Medium | 1.000 |
| task_3_hard | Hard | 1.000 |
| **Overall** | | **1.000** |

## 🔧 Setup

### Local Development
```bash
git clone https://huggingface.co/spaces/kabbie29/email-triage-env
cd email-triage-env
pip install fastapi uvicorn pydantic openai huggingface_hub requests
uvicorn server:app --host 0.0.0.0 --port 7860
```

### Docker
```bash
docker build -t email-triage-env .
docker run -p 7860:7860 email-triage-env
```

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/reset` | POST | Start a fresh episode |
| `/step` | POST | Submit an action |
| `/state` | GET | Get current state |
| `/tasks` | GET | List all tasks |

## 📥 Action Spaces

**Task 1 — Classification:**
```json
{"category": "billing|technical|general|complaint", "priority": "low|medium|high"}
```

**Task 2 — Extraction:**
```json
{"name": "string", "issue": "string", "urgency": "low|medium|high"}
```

**Task 3 — Response:**
```json
{"reply": "string"}
```

## 📤 Observation Space
```json
{
  "task": "string",
  "difficulty": "easy|medium|hard",
  "email": {
    "subject": "string",
    "body": "string"
  },
  "instruction": "string"
}
```

## 🏆 Reward Function

- Range: `0.0` to `1.0`
- **Task 1:** 0.7 for correct category + 0.3 for correct priority
- **Task 2:** 0.33 per correctly extracted field (name, issue, urgency)
- **Task 3:** Equal points per required element found in reply
- Partial credit awarded at every step — never binary!

## 🔁 Running Baseline Inference
```bash
export API_BASE_URL=https://router.huggingface.co/groq/openai/v1
export MODEL_NAME=llama-3.3-70b-versatile
export HF_TOKEN=your_hf_token_here
export SERVER_URL=https://kabbie29-email-triage-env.hf.space
python inference.py
```

## 📁 Project Structure
```
├── environment.py   # Core environment (reset, step, state)
├── tasks.py         # Task definitions and sample emails
├── graders.py       # Scoring logic for each task
├── server.py        # FastAPI web server
├── inference.py     # Baseline inference script
├── openenv.yaml     # OpenEnv specification
├── Dockerfile       # Container definition
└── README.md        # This file
```

## ⚙️ Environment Variables

| Variable | Description |
|----------|-------------|
| `API_BASE_URL` | LLM API endpoint |
| `MODEL_NAME` | Model identifier |
| `HF_TOKEN` | HuggingFace API token |
| `SERVER_URL` | Environment server URL |