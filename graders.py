# graders.py — Scoring logic for each task

def grade_task_1(agent_response: dict, correct_answer: dict) -> float:
    score = 0.0
    agent_category = agent_response.get("category", "").lower().strip()
    agent_priority = agent_response.get("priority", "").lower().strip()
    if agent_category == correct_answer["correct_category"]:
        score += 0.7
    if agent_priority == correct_answer["correct_priority"]:
        score += 0.3
    return round(score, 2)


def grade_task_2(agent_response: dict, correct_answer: dict) -> float:
    score = 0.0
    agent_name = agent_response.get("name", "").lower().strip()
    correct_name = correct_answer["correct_name"].lower()
    if any(part in agent_name for part in correct_name.split()):
        score += 0.33
    agent_issue = agent_response.get("issue", "").lower().strip()
    correct_issue = correct_answer["correct_issue"].lower()
    if any(word in agent_issue for word in correct_issue.split()):
        score += 0.33
    agent_urgency = agent_response.get("urgency", "").lower().strip()
    if agent_urgency == correct_answer["correct_urgency"]:
        score += 0.34
    return round(score, 2)


def grade_task_3(agent_response: dict, email: dict) -> float:
    """
    Task 3: Hard — Professional Email Response
    Strict multi-dimensional grading:
    1. Required elements present        (0.30)
    2. Specificity — references email details  (0.25)
    3. Conciseness — reply under 100 words     (0.20)
    4. Professional tone                (0.15)
    5. Clear next steps with timeline   (0.10)
    """
    reply = agent_response.get("reply", "").strip()
    if not reply:
        return 0.0

    reply_lower = reply.lower()
    words = reply.split()
    word_count = len(words)
    score = 0.0

    # ── 1. Required elements (0.30) ──────────────────────────
    required_elements = email.get("required_elements", [])
    element_keywords = {
        "apology": ["sorry", "apologize", "apologies", "regret"],
        "order_reference": ["order", "#", "45231", "reference"],
        "timeline": ["days", "hours", "week", "within", "by"],
        "next_steps": ["will", "team", "process", "contact", "reach out"],
        "workaround": ["alternatively", "meanwhile", "can also", "try", "send", "email"],
        "resolution_timeline": ["24 hours", "48 hours", "1-2 days", "within", "shortly"],
        "acknowledgement": ["understand", "received", "noted", "see that", "aware"],
        "replacement_offer": ["replace", "send", "new", "exchange", "ship", "reship"],
        "urgency_acknowledgement": ["friday", "urgent", "priority", "immediately", "expedite", "asap"]
    }
    if required_elements:
        points_per_element = 0.30 / len(required_elements)
        for element in required_elements:
            keywords = element_keywords.get(element, [])
            if any(kw in reply_lower for kw in keywords):
                score += points_per_element

    # ── 2. Specificity — must reference specific details (0.25) ──
    specificity_score = 0.0
    subject = email.get("subject", "").lower()
    body = email.get("body", "").lower()

    # Extract key specific words from email (nouns, numbers, names)
    import re
    specific_terms = re.findall(r'\b([A-Z][a-z]+|\d+|#\d+)\b', email.get("body", "") + " " + email.get("subject", ""))
    specific_terms = [t.lower() for t in specific_terms]

    matched_specific = sum(1 for term in specific_terms if term in reply_lower)
    if matched_specific >= 3:
        specificity_score = 0.25
    elif matched_specific == 2:
        specificity_score = 0.15
    elif matched_specific == 1:
        specificity_score = 0.08
    score += specificity_score

    # ── 3. Conciseness — under 100 words (0.20) ──────────────
    if word_count <= 60:
        score += 0.20
    elif word_count <= 80:
        score += 0.15
    elif word_count <= 100:
        score += 0.10
    elif word_count <= 130:
        score += 0.05
    else:
        score += 0.0  # penalize overly long replies

    # ── 4. Professional tone (0.15) ──────────────────────────
    professional_phrases = [
        "dear", "sincerely", "regards", "thank you", "we apologize",
        "please", "kindly", "we understand", "we appreciate"
    ]
    unprofessional_phrases = [
        "hey", "hi there", "no problem", "totally", "basically",
        "honestly", "look,", "listen,", "whatever"
    ]
    professional_hits = sum(1 for p in professional_phrases if p in reply_lower)
    unprofessional_hits = sum(1 for p in unprofessional_phrases if p in reply_lower)

    if unprofessional_hits > 0:
        score += 0.0
    elif professional_hits >= 3:
        score += 0.15
    elif professional_hits == 2:
        score += 0.10
    elif professional_hits == 1:
        score += 0.05

    # ── 5. Clear next steps with timeline (0.10) ─────────────
    timeline_patterns = [
        r'\d+\s*(hours?|days?|weeks?)',
        r'within\s+\d+',
        r'by\s+(monday|tuesday|wednesday|thursday|friday|tomorrow)',
        r'(24|48|72)\s*hours?',
        r'1-2\s*days?',
        r'2-3\s*days?'
    ]
    has_timeline = any(re.search(p, reply_lower) for p in timeline_patterns)
    has_next_step = any(phrase in reply_lower for phrase in [
        "we will", "we'll", "you will receive", "our team will",
        "we are going to", "expect", "you can expect"
    ])
    if has_timeline and has_next_step:
        score += 0.10
    elif has_timeline or has_next_step:
        score += 0.05

    return round(min(score, 1.0), 2)