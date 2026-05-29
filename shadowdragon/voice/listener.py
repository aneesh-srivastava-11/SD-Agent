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
        """Always runs in background with self-healing reconnection logic."""
        error_count = 0
        while self.running:
            try:
                data = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
                self.frames.append(data)
                error_count = 0  # Reset error count on success
            except Exception as e:
                error_count += 1
                time.sleep(0.1)
                if error_count > 10:
                    print("Warning: Audio input stream error. Attempting to restart device...")
                    try:
                        self.stream.stop_stream()
                        self.stream.close()
                    except:
                        pass
                    try:
                        self.stream = self.pa.open(
                            format=pyaudio.paInt16,
                            channels=1,
                            rate=SAMPLE_RATE,
                            input=True,
                            frames_per_buffer=CHUNK_SIZE
                        )
                        print("Audio stream restarted successfully.")
                        error_count = 0
                    except Exception as restart_error:
                        print(f"Failed to restart audio stream: {restart_error}")
                        time.sleep(2.0)  # Wait longer before trying again

    def clear_buffer(self):
        """Flush the audio frame queue to prevent microphone feedback from TTS speaker."""
        self.frames.clear()

    def listen(self, duration=2, use_base=True):
        # For wake words, we only need a shorter slice to be faster
        effective_duration = duration if use_base else 1.5
        
        # Wait for the buffer to have enough data
        time.sleep(0.5) 
        
        num_frames = int(SAMPLE_RATE / CHUNK_SIZE * effective_duration)
        buffer_copy = list(self.frames)
        audio_clip = buffer_copy[-num_frames:] if len(buffer_copy) > num_frames else buffer_copy
        
        if not audio_clip:
            return ""

        # Energy threshold check
        raw_bytes = b''.join(audio_clip)
        audio_np = np.frombuffer(raw_bytes, dtype=np.int16)
        # Increase threshold to ignore faint background noise
        if np.max(np.abs(audio_np)) < 800: 
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
            # condition_on_previous_text=False helps stop hallucinations
            result = model.transcribe(tmp_path, fp16=False, language="en", condition_on_previous_text=False)
            
            text = result["text"].strip()
            
            # Filter common Whisper hallucinations on ambient noise
            low_text = text.lower().strip(" .!?*,")
            hallucinations = ["thank you", "thanks for watching", "subscribe", "bye", "you", "am i recording", "i'm not sure", "let's go"]
            if low_text in hallucinations or len(low_text) < 2:
                return ""
                
            if text:
                print(f"Heard: '{text}'")
            return text
        except Exception as e:
            return ""
        finally:
            if tmp_path and os.path.exists(tmp_path):
                # Robust retry-loop to handle file locks on Windows
                for _ in range(5):
                    try:
                        os.unlink(tmp_path)
                        break
                    except PermissionError:
                        time.sleep(0.1)
                    except:
                        break

    def stop(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()
