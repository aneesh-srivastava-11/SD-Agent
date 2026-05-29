import json
import requests
from shadowdragon.config import MISTRAL_MODEL, SHADOWDRAGON_SYSTEM_PROMPT, GEMINI_API_KEY, GEMINI_MODEL

class MistralAgent:
    def __init__(self, ollama_url="http://localhost:11434/api/generate"):
        self.url = ollama_url
        self.model = MISTRAL_MODEL
        self.system_prompt = SHADOWDRAGON_SYSTEM_PROMPT

    def ask(self, query, context="", history=[]):
        # Try Gemini First
        if GEMINI_API_KEY:
            try:
                gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
                headers = {"Content-Type": "application/json"}
                
                # Build contents list
                contents = []
                for turn in history:
                    contents.append({
                        "role": "user",
                        "parts": [{"text": turn["user"]}]
                    })
                    contents.append({
                        "role": "model",
                        "parts": [{"text": turn["assistant"]}]
                    })
                
                # Add current turn with context
                user_content = ""
                if context:
                    user_content += f"Context/Memory:\n{context}\n\n"
                user_content += query
                
                contents.append({
                    "role": "user",
                    "parts": [{"text": user_content}]
                })
                
                payload = {
                    "contents": contents,
                    "systemInstruction": {
                        "parts": [{"text": self.system_prompt}]
                    }
                }
                
                response = requests.post(gemini_url, headers=headers, json=payload, timeout=10)
                response.raise_for_status()
                result = response.json()
                
                candidates = result.get("candidates", [])
                if candidates:
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
            except Exception as e:
                print(f"Gemini agent ask failed: {e}. Falling back to Mistral (Ollama)...")

        # Fallback to local Ollama (Mistral)
        full_prompt = f"{self.system_prompt}\n\n{context}\n\n"
        for turn in history:
            full_prompt += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"
        full_prompt += f"User: {query}\nAssistant:"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False
        }
        try:
            response = requests.post(self.url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            print(f"Error in Mistral Agent: {e}")
            return "I'm sorry, I'm having trouble thinking right now."

    def generate_plan(self, task, available_tools):
        # Try Gemini First
        if GEMINI_API_KEY:
            try:
                gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
                headers = {"Content-Type": "application/json"}
                
                plan_prompt = f"""
                Task: {task}
                Available Tools: {available_tools}
                
                Generate a step-by-step numbered plan to execute this task. 
                Each step should correspond to a tool call if possible.
                """
                
                payload = {
                    "contents": [
                        {
                            "parts": [{"text": plan_prompt}]
                        }
                    ],
                    "systemInstruction": {
                        "parts": [{"text": self.system_prompt}]
                    }
                }
                response = requests.post(gemini_url, headers=headers, json=payload, timeout=10)
                response.raise_for_status()
                result = response.json()
                
                candidates = result.get("candidates", [])
                if candidates:
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
            except Exception as e:
                print(f"Gemini agent plan generation failed: {e}. Falling back to Mistral (Ollama)...")

        # Fallback to local Ollama (Mistral)
        plan_prompt = f"""
        {self.system_prompt}
        Task: {task}
        Available Tools: {available_tools}
        
        Generate a step-by-step numbered plan to execute this task. 
        Each step should correspond to a tool call if possible.
        """
        payload = {
            "model": self.model,
            "prompt": plan_prompt,
            "stream": False
        }
        try:
            response = requests.post(self.url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            print(f"Error generating plan: {e}")
            return "1. analyze_task"
