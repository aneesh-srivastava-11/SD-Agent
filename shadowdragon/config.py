import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Ollama Models (Fallback)
PHI3_MODEL = "phi3:mini"
MISTRAL_MODEL = "mistral"

# System Prompts
SHADOWDRAGON_SYSTEM_PROMPT = """
You are ShadowDragon, a calm and intelligent AI assistant that speaks naturally and concisely. 
You have access to system tools and memory. Be helpful, efficient, and maintain a sophisticated tone.
"""

ROUTER_SYSTEM_PROMPT = """
Classify the user command into one of these categories:
SYSTEM_COMMAND
AI_TASK
START_CONVERSATION
END_CONVERSATION
MEMORY_WRITE
MEMORY_READ

Return ONLY the label.
"""

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "memory", "memory.json")

# Voice Settings
WAKE_WORD = "shadowdragon"
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024

# External Binary Paths
PIPER_EXE = "piper"  # Can be 'piper' if installed via pip, or path to piper.exe
PIPER_MODEL = "en_US-john-medium.onnx"

# OCR (Tesseract) Settings
TESSER_EXE = os.getenv("TESSER_EXE")
if not TESSER_EXE or not os.path.exists(TESSER_EXE):
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\ANEESH\Desktop\SDA\tesseract.exe"
    ]
    for path in common_paths:
        if os.path.exists(path):
            TESSER_EXE = path
            break
    else:
        TESSER_EXE = "tesseract"

