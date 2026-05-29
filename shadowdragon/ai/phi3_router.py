import json
import requests
from shadowdragon.config import PHI3_MODEL, ROUTER_SYSTEM_PROMPT, GEMINI_API_KEY, GEMINI_MODEL

class Phi3Router:
    def __init__(self, ollama_url="http://localhost:11434/api/generate"):
        self.url = ollama_url
        self.model = PHI3_MODEL

    def classify_intent(self, text):
        valid_intents = ["SYSTEM_COMMAND", "AI_TASK", "START_CONVERSATION", "END_CONVERSATION", "MEMORY_WRITE", "MEMORY_READ"]
        
        # Try Gemini First
        if GEMINI_API_KEY:
            try:
                gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": f"Command: {text}"}
                            ]
                        }
                    ],
                    "systemInstruction": {
                        "parts": [
                            {"text": ROUTER_SYSTEM_PROMPT}
                        ]
                    }
                }
                response = requests.post(gemini_url, headers=headers, json=payload, timeout=5)
                response.raise_for_status()
                result = response.json()
                
                # Extract text
                candidates = result.get("candidates", [])
                if candidates:
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    if parts:
                        intent = parts[0].get("text", "").strip().upper()
                        for valid in valid_intents:
                            if valid in intent:
                                return valid
            except Exception as e:
                print(f"Gemini routing failed: {e}. Falling back to Phi-3 (Ollama)...")
        
        # Fallback to local Ollama (Phi-3)
        prompt = f"{ROUTER_SYSTEM_PROMPT}\n\nCommand: {text}"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(self.url, json=payload, timeout=5)
            response.raise_for_status()
            intent = response.json().get("response", "").strip().upper()
            for valid in valid_intents:
                if valid in intent:
                    return valid
            return "AI_TASK" # Default
        except Exception as e:
            print(f"Error in Phi-3 Router: {e}")
            return "AI_TASK"
