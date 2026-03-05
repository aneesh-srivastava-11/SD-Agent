import subprocess
import os
from shadowdragon.config import PIPER_EXE, PIPER_MODEL

class VoiceSpeech:
    def __init__(self):
        self.piper_exe = PIPER_EXE
        self.model = PIPER_MODEL
        # Try to find piper in python scripts if directly calling 'piper' fails
        if self.piper_exe == "piper":
            import sys
            import os
            scripts_dir = os.path.join(os.path.dirname(sys.executable), "Scripts")
            potential_piper = os.path.join(scripts_dir, "piper.exe")
            if os.path.exists(potential_piper):
                self.piper_exe = potential_piper

    def speak(self, text):
        if not text:
            return
        print(f"ShadowDragon: {text}")
        try:
            # Command: echo "text" | piper --model model.onnx --output_raw | aplay (or similar for windows)
            # On Windows, we can output to a wav and play it, or pipe to a player.
            # Simplified for now: pipe to piper and play output via subprocess.
            # Note: This assumes piper and a player like 'ffplay' or 'aplay' is available or piped correctly.
            # Using a temporary wav file for maximum compatibility on Windows.
            wav_path = "response.wav"
            cmd = f'echo {text} | {self.piper_exe} --model {self.model} --output_file {wav_path}'
            subprocess.run(cmd, shell=True, check=True)
            
            # Use start to play wav on Windows
            os.system(f"start /min powershell -c (New-Object Media.SoundPlayer '{wav_path}').PlaySync()")
        except Exception as e:
            print(f"Error in TTS: {e}")
            # Fallback to simple print if TTS fails
