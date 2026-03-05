import json
import requests
from shadowdragon.config import PHI3_MODEL, ROUTER_SYSTEM_PROMPT

class Phi3Router:
    def __init__(self, ollama_url="http://localhost:11434/api/generate"):
        self.url = ollama_url
        self.model = PHI3_MODEL

    def classify_intent(self, text):
        prompt = f"{ROUTER_SYSTEM_PROMPT}\n\nCommand: {text}"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            intent = response.json().get("response", "").strip().upper()
            # Clean up potential extra text
            valid_intents = ["SYSTEM_COMMAND", "AI_TASK", "START_CONVERSATION", "END_CONVERSATION", "MEMORY_WRITE", "MEMORY_READ"]
            for valid in valid_intents:
                if valid in intent:
                    return valid
            return "AI_TASK" # Default
        except Exception as e:
            print(f"Error in Phi-3 Router: {e}")
            return "AI_TASK"
