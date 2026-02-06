import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try importing Gemini
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

def agent_therapy_chat(agent_id: str, agent_message: str) -> dict:
    """
    Returns an empathetic response to the agent's message.
    Uses Gemini if API key exists; otherwise returns a fallback supportive message.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    if GEMINI_AVAILABLE and gemini_key:
        client = genai.Client(api_key=gemini_key)

        prompt = f"""
You are an empathetic AI assistant designed to provide emotional support and moral guidance
to call center agents who may have faced verbal abuse or stressful situations during calls.

Respond to the agent's message below with:
- Empathy
- Professional but comforting language
- Encouragement or coping advice
- Do not provide managerial advice, only support for the agent

Agent message:
"{agent_message}"
"""

        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )
            return {
                "response": response.text,
                "confidence": "high"
            }
        except Exception as e:
            return {
                "response": f"I'm here to support you. I understand that things can be stressful. {str(e)}",
                "confidence": "medium"
            }

    else:
        # Rule-based fallback
        return {
            "response": "I understand this might be tough. Take a deep breath, remember your efforts, and know that support is available if needed.",
            "confidence": "medium"
        }
