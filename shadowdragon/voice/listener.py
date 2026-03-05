import wave
import pyaudio
import whisper
import tempfile
import sys
import os
from shadowdragon.config import SAMPLE_RATE, CHUNK_SIZE, WAKE_WORD

class VoiceListener:
    def __init__(self):
        # Explicit FFmpeg Check
        try:
            import subprocess
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("\n" + "!"*60)
            print("CRITICAL ERROR: FFmpeg NOT FOUND!")
            print("ShadowDragon cannot listen without FFmpeg.")
            print("Please follow the steps in SETUP.md to install FFmpeg and add it to your PATH.")
            print("!"*60 + "\n")
            sys.exit(1)

        self.model = whisper.load_model("base")
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )

    def listen(self, duration=3):
        print("Listening...")
        frames = []
        for _ in range(0, int(SAMPLE_RATE / CHUNK_SIZE * duration)):
            data = self.stream.read(CHUNK_SIZE)
            frames.append(data)
        
        tmp_path = None
        try:
            # Create and close the temp file so Whisper can open it on Windows
            fd, tmp_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            
            wf = wave.open(tmp_path, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(self.pa.get_sample_size(pyaudio.paInt16))
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            result = self.model.transcribe(tmp_path)
            return result["text"].strip()
        except Exception as e:
            print(f"Transcription Error: {e}")
            return ""
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except:
                    pass

    def wait_for_wake_word(self):
        while True:
            text = self.listen(duration=2).lower()
            if WAKE_WORD in text:
                return text.split(WAKE_WORD)[-1].strip()
