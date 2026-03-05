import os
import wave
import pyaudio
import whisper
import tempfile
from shadowdragon.config import SAMPLE_RATE, CHUNK_SIZE, WAKE_WORD

class VoiceListener:
    def __init__(self):
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
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            wf = wave.open(tmp_file.name, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(self.pa.get_sample_size(pyaudio.paInt16))
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            result = self.model.transcribe(tmp_file.name)
            os.unlink(tmp_file.name)
            return result["text"].strip()

    def wait_for_wake_word(self):
        while True:
            text = self.listen(duration=2).lower()
            if WAKE_WORD in text:
                return text.split(WAKE_WORD)[-1].strip()
