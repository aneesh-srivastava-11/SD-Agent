import os
import sys
import threading
import time
import requests
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
from shadowdragon.config import WAKE_WORD, GEMINI_API_KEY

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
        
        self.gui = None
        self.hotkey_triggered = False
        self.running = True
        
        # Start global Windows hotkey listener in background
        self.start_hotkey_listener()

    def start_hotkey_listener(self):
        """Registers global Windows hotkey Alt+Shift+S via Win32 API without external libraries."""
        def hotkey_loop():
            import ctypes
            from ctypes import wintypes
            
            user32 = ctypes.windll.user32
            HOTKEY_ID = 1
            # Modifiers: Alt=0x0001, Shift=0x0004
            MOD_ALT = 0x0001
            MOD_SHIFT = 0x0004
            VK_S = 0x53  # Virtual key code for 'S'
            
            if not user32.RegisterHotKey(None, HOTKEY_ID, MOD_ALT | MOD_SHIFT, VK_S):
                print("Hotkey Alt+Shift+S failed to register.")
                return
            
            try:
                msg = wintypes.MSG()
                while self.running:
                    # GetMessage blocks until a window message is posted
                    if user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                        if msg.message == 0x0312 and msg.wParam == HOTKEY_ID:
                            print("Hotkey Alt+Shift+S pressed! Triggering voice listening.")
                            self.hotkey_triggered = True
                        user32.TranslateMessage(ctypes.byref(msg))
                        user32.DispatchMessageW(ctypes.byref(msg))
            except Exception as e:
                print(f"Hotkey listener exception: {e}")
            finally:
                user32.UnregisterHotKey(None, HOTKEY_ID)
                
        threading.Thread(target=hotkey_loop, daemon=True).start()

    def log_conversation(self, role, text):
        """Append conversational turns to local log file."""
        try:
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "chat_history.txt")
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {role}: {text}\n")
        except Exception as e:
            print(f"Failed to write conversation logs: {e}")

    def run(self):
        print("ShadowDragon is online.")
        
        # Verify brain configuration
        if GEMINI_API_KEY:
            print("Status: Gemini API configuration detected. Using Gemini as the primary LLM.")
            try:
                requests.get("http://localhost:11434", timeout=1)
                print("Status: Ollama is running and available as a fallback.")
            except:
                print("Notice: Ollama is not running. Local fallback will not be available.")
        else:
            print("WARNING: GEMINI_API_KEY is not set. Defaulting to local LLMs (Ollama).")
            try:
                requests.get("http://localhost:11434", timeout=1)
            except:
                print("CRITICAL: Ollama is NOT running! Please start the Ollama app.")
                self.speech.speak("Warning: My brain is offline. Please start Ollama.")

        self.speech.speak("ShadowDragon is online.")
        
        while self.running:
            command = ""
            
            # Check if hotkey triggered manual listen
            if self.hotkey_triggered:
                self.hotkey_triggered = False
                if self.gui:
                    self.gui.update_status("Listening (via hotkey)...", "#00f0ff")
                self.speech.speak("Yes?")
                self.listener.clear_buffer()
                command = self.listener.listen(duration=4.0, use_base=True)
            else:
                # Stage 1: Wait for wake word ("shadow")
                if not self.conv_mgr.is_active:
                    if self.gui:
                        self.gui.update_status("Waiting for Wake Word (say 'shadow' or Alt+Shift+S)...", "#8f9099")
                    print("Waiting for wake word (say 'shadow')...")
                    text = self.listener.listen(duration=1.5, use_base=False).lower()
                    
                    if not text:
                        continue
                    
                    if "shadow" in text:
                        command = text.split("shadow")[-1].strip()
                        if not command or len(command) < 3:
                            if self.gui:
                                self.gui.update_status("Listening...", "#00f0ff")
                            self.speech.speak("Yes?")
                            self.listener.clear_buffer()
                            command = self.listener.listen(duration=4.0, use_base=True)
                    else:
                        continue
                else:
                    # Conversation mode - active listening
                    if self.gui:
                        self.gui.update_status("Listening...", "#00f0ff")
                    print("Listening for input...")
                    command = self.listener.listen(duration=4.0, use_base=True)
            
            if not command:
                continue
            
            print(f"User: {command}")
            if self.gui:
                self.gui.add_log("user", command)
            self.log_conversation("User", command)
            
            # Stage 2: Intent Classification
            if self.gui:
                self.gui.update_status("Thinking...", "#ffcc00")
            intent = self.router.classify_intent(command)
            print(f"Intent: {intent}")
            
            # Stage 3: Routing
            self.process_intent(intent, command)

    def process_intent(self, intent, command):
        # Normalize command for checks
        cmd_lower = command.lower()
        cmd_clean = cmd_lower.replace("shadow dragon", "").replace("shadowdragon", "").strip()
        
        response = ""
        
        if intent == "START_CONVERSATION" or "talk" in cmd_lower:
            self.conv_mgr.start()
            response = "Sure. What would you like to talk about?"
            
        elif intent == "END_CONVERSATION" or "stop talking" in cmd_lower:
            self.conv_mgr.stop()
            response = "Stopping conversation mode."
            
        elif self.conv_mgr.is_active or intent == "AI_TASK":
            context = self.memory.get_all_context()
            history = self.conv_mgr.get_history()
            response = self.agent.ask(cmd_clean if cmd_clean else command, context=context, history=history)
            if self.conv_mgr.is_active:
                self.conv_mgr.add_turn(command, response)
                
        elif intent == "SYSTEM_COMMAND":
            # Detect app launch or terminal or browser
            if any(k in cmd_lower for k in ["start", "open", "launch"]):
                app_name = cmd_lower.replace("start", "").replace("open", "").replace("launch", "").strip()
                app_name = app_name.replace("browser", "").strip()
                response = self.app_launcher.launch(app_name)
            elif any(k in cmd_lower for k in ["run", "git", "terminal"]):
                cmd = cmd_lower.replace("run", "").replace("terminal", "").strip()
                response = self.terminal.run_command(cmd)
            elif any(k in cmd_lower for k in ["website", "go to", "browse"]):
                url = cmd_lower.replace("website", "").replace("go to", "").replace("browse", "").strip()
                response = self.browser.open_url(url)
            else:
                response = self.agent.ask(f"The user wants me to do a system command: '{command}'. What should I do? Reply concisely.")

        elif intent == "MEMORY_WRITE":
            parts = command.lower().split("is")
            if len(parts) > 1:
                key = parts[0].replace("remember", "").strip()
                val = parts[1].strip()
                self.memory.save_memory(key, val)
                response = f"I've remembered that {key} is {val}."
                if self.gui:
                    self.gui.refresh_memory()
            else:
                response = "I couldn't quite catch what I should remember."

        elif intent == "MEMORY_READ":
            key = command.replace("what is", "").strip()
            val = self.memory.get_memory(key)
            response = f"You told me it is {val}."

        # Output the response
        if response:
            if self.gui:
                self.gui.update_status("Speaking...", "#00ff66")
                self.gui.add_log("agent", response)
            self.log_conversation("Agent", response)
            self.speech.speak(response)
            
            # Flush the mic queue right after TTS output finishes to prevent audio echo/feedback loops
            self.listener.clear_buffer()

if __name__ == "__main__":
    assistant = ShadowDragon()
    try:
        # Run voice loop in a background daemon thread
        voice_thread = threading.Thread(target=assistant.run, daemon=True)
        voice_thread.start()
        
        # Run Tkinter GUI Dashboard on the main thread
        from shadowdragon.gui import ShadowDragonGUI
        gui = ShadowDragonGUI(assistant)
        gui.run()
    except Exception as e:
        print(f"Failed to start GUI Dashboard: {e}. Running in console-only mode.")
        assistant.run()
