# graders.py — Scoring logic for each task

def grade_task_1(agent_response: dict, correct_answer: dict) -> float:
    """
    Task 1: Email Classification
    Score: 0.7 for correct category + 0.3 for correct priority
    """
    score = 0.0

    agent_category = agent_response.get("category", "").lower().strip()
    agent_priority = agent_response.get("priority", "").lower().strip()

    if agent_category == correct_answer["correct_category"]:
        score += 0.7

    if agent_priority == correct_answer["correct_priority"]:
        score += 0.3

    return round(score, 2)


def grade_task_2(agent_response: dict, correct_answer: dict) -> float:
    """
    Task 2: Info Extraction
    Score: 0.33 per correct field (name, issue, urgency)
    """
    score = 0.0

    # Check name — flexible matching
    agent_name = agent_response.get("name", "").lower().strip()
    correct_name = correct_answer["correct_name"].lower()
    if any(part in agent_name for part in correct_name.split()):
        score += 0.33

    # Check issue type
    agent_issue = agent_response.get("issue", "").lower().strip()
    correct_issue = correct_answer["correct_issue"].lower()
    if any(word in agent_issue for word in correct_issue.split()):
        score += 0.33

    # Check urgency
    agent_urgency = agent_response.get("urgency", "").lower().strip()
    if agent_urgency == correct_answer["correct_urgency"]:
        score += 0.34

    return round(score, 2)


def grade_task_3(agent_response: dict, required_elements: list) -> float:
    """
    Task 3: Response Drafting
    Score: equal points per required element found in the reply
    """
    response_text = agent_response.get("reply", "").lower()

    if not response_text:
        return 0.0

    element_keywords = {
        "apology": ["sorry", "apologize", "apologies", "regret"],
        "order_reference": ["order", "#", "reference", "45231"],
        "timeline": ["days", "hours", "week", "by", "within"],
        "next_steps": ["will", "team", "process", "contact", "reach"],
        "workaround": ["alternatively", "meanwhile", "can also", "try", "send"],
        "resolution_timeline": ["days", "hours", "soon", "shortly", "within"],
        "acknowledgement": ["understand", "received", "noted", "see that"],
        "replacement_offer": ["replace", "send", "new", "exchange", "ship"],
        "urgency_acknowledgement": ["friday", "urgent", "priority", "immediately", "asap"]
    }

    points_per_element = 1.0 / len(required_elements)
    score = 0.0

    for element in required_elements:
        keywords = element_keywords.get(element, [])
        if any(keyword in response_text for keyword in keywords):
            score += points_per_element

    return round(score, 2)