import os
import sys
import threading
from shadowdragon.ai.phi3_router import Phi3Router
from shadowdragon.ai.mistral_agent import MistralAgent
from shadowdragon.ai.conversation_manager import ConversationManager
from shadowdragon.memory.memory_store import MemoryStore
from shadowdragon.voice.listener import VoiceListener
from shadowdragon.voice.speech import VoiceSpeech
from shadowdragon.tools.app_launcher import AppLauncher
from shadowdragon.tools.browser import BrowserTools
from shadowdragon.tools.terminal import TerminalTools
from shadowdragon.tools.screen_tools import ScreenTools
from shadowdragon.config import WAKE_WORD

class ShadowDragon:
    def __init__(self):
        self.router = Phi3Router()
        self.agent = MistralAgent()
        self.conv_mgr = ConversationManager()
        self.memory = MemoryStore()
        self.listener = VoiceListener()
        self.speech = VoiceSpeech()
        
        # Tools
        self.app_launcher = AppLauncher()
        self.browser = BrowserTools()
        self.terminal = TerminalTools()
        self.screen = ScreenTools()
        
        self.available_tools = ["launch_application", "open_website", "run_terminal_command", "read_screen", "analyze_screen", "memory_write", "memory_read"]

    def run(self):
        print("ShadowDragon is online.")
        self.speech.speak("ShadowDragon is online.")
        
        while True:
            # Stage 1: Continuous Listening for Wake Word or Conversation Mode
            if not self.conv_mgr.is_active:
                print(f"Waiting for wake word '{WAKE_WORD}'...")
                text = self.listener.listen(duration=2).lower()
                if WAKE_WORD not in text:
                    continue
                command = text.split(WAKE_WORD)[-1].strip()
            else:
                # Conversation mode - active listening
                command = self.listener.listen(duration=3)
            
            if not command:
                continue
            
            print(f"User: {command}")
            
            # Stage 2: Intent Classification
            intent = self.router.classify_intent(command)
            print(f"Intent: {intent}")
            
            # Stage 3: Routing
            self.process_intent(intent, command)

    def process_intent(self, intent, command):
        if intent == "START_CONVERSATION":
            self.conv_mgr.start()
            response = "Sure. What would you like to talk about?"
            self.speech.speak(response)
            
        elif intent == "END_CONVERSATION" or "stop talking" in command.lower():
            self.conv_mgr.stop()
            self.speech.speak("Stopping conversation mode.")
            
        elif self.conv_mgr.is_active or intent == "AI_TASK":
            context = self.memory.get_all_context()
            history = self.conv_mgr.get_history()
            response = self.agent.ask(command, context=context, history=history)
            self.speech.speak(response)
            if self.conv_mgr.is_active:
                self.conv_mgr.add_turn(command, response)
                
        elif intent == "SYSTEM_COMMAND":
            # Detect app launch or terminal or browser
            if "start" in command or "open" in command or "launch" in command:
                app_name = command.replace("start", "").replace("open", "").replace("launch", "").strip()
                result = self.app_launcher.launch(app_name)
                self.speech.speak(result)
            elif "run" in command or "git" in command:
                cmd = command.replace("run", "").strip()
                result = self.terminal.run_command(cmd)
                self.speech.speak("Command executed.")
            elif "website" in command or "go to" in command:
                url = command.replace("website", "").replace("go to", "").strip()
                result = self.browser.open_url(url)
                self.speech.speak(result)
            else:
                self.speech.speak("I'm not sure how to execute that system command yet.")

        elif intent == "MEMORY_WRITE":
            # Simple parsing: "remember my project name is Atlas"
            parts = command.lower().split("is")
            if len(parts) > 1:
                key = parts[0].replace("remember", "").strip()
                val = parts[1].strip()
                self.memory.save_memory(key, val)
                self.speech.speak(f"I've remembered that {key} is {val}.")
            else:
                self.speech.speak("I couldn't quite catch what I should remember.")

        elif intent == "MEMORY_READ":
            key = command.replace("what is", "").strip()
            val = self.memory.get_memory(key)
            self.speech.speak(f"You told me it is {val}.")

if __name__ == "__main__":
    assistant = ShadowDragon()
    assistant.run()
