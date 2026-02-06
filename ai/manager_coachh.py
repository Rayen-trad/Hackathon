import os
import json
from typing import List

SUMMARIES_DIR = "data/summaries"


def load_agent_summaries(agent_id: str, limit: int = 5) -> List[dict]:
    agent_dir = os.path.join(SUMMARIES_DIR, agent_id)
    if not os.path.exists(agent_dir):
        return []

    files = sorted(
        [f for f in os.listdir(agent_dir) if f.endswith("_summary.json")],
        reverse=True
    )

    summaries = []
    for file in files[:limit]:
        with open(os.path.join(agent_dir, file), "r", encoding="utf-8") as f:
            summaries.append(json.load(f))

    return summaries


def coach_manager(agent_id: str, manager_question: str) -> dict:
    summaries = load_agent_summaries(agent_id)

    if not summaries:
        return {
            "response": "No incident history is available for this agent yet.",
            "confidence": "low"
        }

    high_risk = any(s.get("risk_level") == "high" for s in summaries)

    response = (
        "Based on recent incident reports, the agent has been exposed to repeated "
        "verbal abuse. It is recommended to acknowledge the agent’s experience, "
        "offer psychological support, and review escalation procedures."
        if high_risk
        else
        "The agent has experienced low to moderate levels of verbal conflict. "
        "Regular check-ins and coaching are advised."
    )

    return {
        "response": response,
        "confidence": "high" if high_risk else "medium",
        "used_reports": len(summaries)
    }
