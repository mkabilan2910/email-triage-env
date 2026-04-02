# tasks.py — All tasks and sample emails for our environment

TASKS = {
    "task_1_easy": {
        "name": "Email Classification",
        "description": "Classify the email into the correct category and priority. Respond with JSON: {category: ..., priority: ...}. Category must be one of: billing, technical, general, complaint. Priority must be one of: low, medium, high.",
        "difficulty": "easy",
        "emails": [
            {
                "id": "e1",
                "subject": "My invoice is wrong",
                "body": "Hi, I was charged twice on my last bill. Please fix this immediately.",
                "correct_category": "billing",
                "correct_priority": "high"
            },
            {
                "id": "e2",
                "subject": "App keeps crashing",
                "body": "Your mobile app crashes every time I try to open it. Very frustrated.",
                "correct_category": "technical",
                "correct_priority": "high"
            },
            {
                "id": "e3",
                "subject": "What are your business hours?",
                "body": "Hello, I just wanted to know what time your support team is available.",
                "correct_category": "general",
                "correct_priority": "low"
            }
        ]
    },

    "task_2_medium": {
        "name": "Email Info Extraction",
        "description": "Extract information from the email. Respond with JSON: {name: ..., issue: ..., urgency: ...}. Urgency must be one of: low, medium, high.",
        "difficulty": "medium",
        "emails": [
            {
                "id": "e4",
                "subject": "Urgent: Payment failed",
                "body": "Hi, my name is Rahul Sharma. My payment of $99 failed three times today. This is urgent as my subscription expires tonight.",
                "correct_name": "Rahul Sharma",
                "correct_issue": "payment failure",
                "correct_urgency": "high"
            },
            {
                "id": "e5",
                "subject": "Login problem",
                "body": "This is Priya Singh. I have been unable to log into my account since yesterday. I tried resetting my password but that didn't work either.",
                "correct_name": "Priya Singh",
                "correct_issue": "login failure",
                "correct_urgency": "medium"
            },
            {
                "id": "e6",
                "subject": "Feature request",
                "body": "Hello, I am Arjun Mehta. I would love it if you could add dark mode to your app. No rush, just a suggestion!",
                "correct_name": "Arjun Mehta",
                "correct_issue": "feature request",
                "correct_urgency": "low"
            }
        ]
    },

    "task_3_hard": {
        "name": "Email Response Drafting",
        "description": "Draft a professional reply to the customer email. Respond with JSON: {reply: ...}. Your reply must be polite, address the issue directly, and include next steps.",
        "difficulty": "hard",
        "emails": [
            {
                "id": "e7",
                "subject": "Refund not received",
                "body": "I requested a refund 2 weeks ago and still haven't received it. Order #45231. This is unacceptable.",
                "required_elements": ["apology", "order_reference", "timeline", "next_steps"]
            },
            {
                "id": "e8",
                "subject": "Cannot download invoice",
                "body": "Hi, I need my invoice for tax purposes but the download button does nothing. Please help ASAP.",
                "required_elements": ["apology", "workaround", "resolution_timeline"]
            },
            {
                "id": "e9",
                "subject": "Wrong item delivered",
                "body": "I ordered a blue shirt size L but received a red shirt size M. I need this fixed before my event on Friday.",
                "required_elements": ["apology", "acknowledgement", "replacement_offer", "urgency_acknowledgement"]
            }
        ]
    }
}