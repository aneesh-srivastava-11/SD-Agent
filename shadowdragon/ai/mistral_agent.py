import json
import requests
from shadowdragon.config import MISTRAL_MODEL, SHADOWDRAGON_SYSTEM_PROMPT

class MistralAgent:
    def __init__(self, ollama_url="http://localhost:11434/api/generate"):
        self.url = ollama_url
        self.model = MISTRAL_MODEL
        self.system_prompt = SHADOWDRAGON_SYSTEM_PROMPT

    def ask(self, query, context="", history=[]):
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
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            print(f"Error in Mistral Agent: {e}")
            return "I'm sorry, I'm having trouble thinking right now."

    def generate_plan(self, task, available_tools):
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
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            print(f"Error generating plan: {e}")
            return "1. analyze_task"
