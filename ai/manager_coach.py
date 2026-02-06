import os
import json
from typing import List
from dotenv import load_dotenv

# Load .env automatically
load_dotenv()

# Try importing Gemini, if available
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

SUMMARIES_DIR = "data/summaries"


def load_agent_summaries(agent_id: str, limit: int = 5) -> List[dict]:
    """Load recent summary files for an agent."""
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
    """Return manager coaching advice. Uses Gemini if API key exists, otherwise fallback."""
    summaries = load_agent_summaries(agent_id)

    if not summaries:
        return {
            "response": "No incident history is available for this agent yet.",
            "confidence": "low"
        }

    gemini_key = os.getenv("GEMINI_API_KEY")
    if GEMINI_AVAILABLE and gemini_key:
        # Use Gemini AI
        client = genai.Client(api_key=gemini_key)
        context = "\n\n".join(
            f"""
Conversation ID: {s['conversation_id']}
Risk Level: {s['risk_level']}
Summary: {s['summary_text']}
Recommendation: {s['recommendation']}
""" for s in summaries
        )

        prompt = f"""
You are an AI advisor helping a call center manager support agents.

Below are incident summaries related to ONE agent.
Use ONLY this information.

Incident history:
{context}

Manager question:
"{manager_question}"

Your response must:
- Be empathetic
- Be professional
- Give clear managerial advice
- Avoid assumptions beyond the reports
"""

        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            return {
                "response": response.text,
                "confidence": "high",
                "used_reports": len(summaries)
            }
        except Exception as e:
            # If API fails, fallback to rule-based
            return {
                "response": f"AI API failed, fallback advice: Based on reports, the agent may need support. {str(e)}",
                "confidence": "medium",
                "used_reports": len(summaries)
            }

    else:
        # Rule-based fallback
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
