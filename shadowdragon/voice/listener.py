import wave
import pyaudio
import whisper
import tempfile
import sys
import os
import threading
import numpy as np
import collections
import time
from shadowdragon.config import SAMPLE_RATE, CHUNK_SIZE

class VoiceListener:
    def __init__(self):
        # 1. FFmpeg Check
        try:
            import subprocess
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except:
            print("CRITICAL: FFmpeg missing.")
            sys.exit(1)

        print("Loading Whisper models (tiny for wake-word, base for logic)...")
        # tiny.en is much faster for just detecting the wake word
        self.wake_model = whisper.load_model("tiny.en")
        self.cmd_model = whisper.load_model("base")
        
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )
        
        # Continuous Background Recording
        self.frames = collections.deque(maxlen=int(SAMPLE_RATE / CHUNK_SIZE * 10)) # 10s buffer
        self.running = True
        self.record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self.record_thread.start()

    def _record_loop(self):
        """Always runs in background to prevent overflow."""
        while self.running:
            try:
                data = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
                self.frames.append(data)
            except:
                pass

    def listen(self, duration=3, use_base=True):
        # Allow buffer to fill for requested duration
        time.sleep(duration)
        
        # Take the LAST 'duration' seconds of audio from the buffer
        num_frames = int(SAMPLE_RATE / CHUNK_SIZE * duration)
        buffer_copy = list(self.frames)
        audio_clip = buffer_copy[-num_frames:] if len(buffer_copy) > num_frames else buffer_copy
        
        if not audio_clip:
            return ""

        # Energy threshold check
        raw_bytes = b''.join(audio_clip)
        audio_np = np.frombuffer(raw_bytes, dtype=np.int16)
        if np.max(np.abs(audio_np)) < 600:
            return ""

        tmp_path = None
        try:
            fd, tmp_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            
            with wave.open(tmp_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(self.pa.get_sample_size(pyaudio.paInt16))
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(raw_bytes)
            
            model = self.cmd_model if use_base else self.wake_model
            result = model.transcribe(tmp_path, fp16=False, language="en")
            
            text = result["text"].strip()
            if text:
                print(f"Heard: '{text}'")
            return text
        except Exception as e:
            return ""
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def stop(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()
