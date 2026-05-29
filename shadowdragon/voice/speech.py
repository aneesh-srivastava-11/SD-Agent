import subprocess
import os
import winsound
from shadowdragon.config import PIPER_EXE, PIPER_MODEL

class VoiceSpeech:
    def __init__(self):
        self.piper_exe = PIPER_EXE
        self.model = PIPER_MODEL
        # Try to find piper in python scripts if directly calling 'piper' fails
        if self.piper_exe == "piper":
            import sys
            import os
            
            # Potential locations
            user_home = os.path.expanduser("~")
            search_paths = [
                os.path.join(os.path.dirname(sys.executable), "Scripts"),
                os.path.join(user_home, "AppData", "Local", "Packages", "PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0", "LocalCache", "local-packages", "Python311", "Scripts")
            ]
            
            for path in search_paths:
                potential_piper = os.path.join(path, "piper.exe")
                if os.path.exists(potential_piper):
                    self.piper_exe = potential_piper
                    break

    def speak(self, text):
        if not text:
            return
        print(f"ShadowDragon: {text}")
        try:
            wav_path = "response.wav"
            
            # Resolve model path
            model_path = self.model
            if not os.path.isabs(model_path):
                # Try relative to shadowdragon folder
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                model_path = os.path.join(base_dir, self.model)
            
            # Securely execute Piper using stdin piping without shell=True
            process = subprocess.Popen(
                [self.piper_exe, "--model", model_path, "--output_file", wav_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Send text to stdin and wait for completion
            stdout, stderr = process.communicate(input=text)
            
            if process.returncode != 0:
                print(f"Piper error: {stderr}")
                return
            
            # Play wav synchronously using native winsound on Windows to block execution and prevent feedback loop
            if os.path.exists(wav_path):
                winsound.PlaySound(wav_path, winsound.SND_FILENAME)
        except Exception as e:
            print(f"Error in TTS: {e}")

