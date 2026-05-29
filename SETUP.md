# ⚙️ ShadowDragon Setup Instructions

ShadowDragon runs on Windows and requires several system dependencies to manage voice recording, text-to-speech, OCR, and AI agent reasoning. Follow this guide to configure your environment.

> [!IMPORTANT]
> **FFmpeg is REQUIRED** for OpenAI Whisper voice recognition. If FFmpeg is missing, the speech-to-text pipeline will throw a `FileNotFoundError` and fail to initialize.

---

## 📋 System Dependencies Setup

### 1. FFmpeg (Required for STT)
Whisper requires FFmpeg to decode recorded audio frames.
1. **Download**: Go to [gyan.dev FFmpeg Builds](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z) and download the essentials package.
2. **Extract**: Extract the contents of the archive to `C:\ffmpeg`.
3. **Add to PATH**:
   - Open the Windows Start Menu, search for **"Edit the system environment variables"**, and press Enter.
   - Click the **Environment Variables...** button.
   - Under **System variables**, select the **Path** variable and click **Edit...**.
   - Click **New** and paste: `C:\ffmpeg\bin`
   - Click **OK** on all open windows to apply the changes.
4. **Restart**: Restart your terminal, CMD, PowerShell, or VS Code for the changes to take effect.

---

### 2. Tesseract OCR (Required for Screen Automation)
To allow the assistant to read and analyze your screen:
1. **Download**: Install the Windows installer from the [UB-Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki).
2. **Installation Path**: By default, it installs to:
   - `C:\Program Files\Tesseract-OCR\tesseract.exe` or
   - `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
3. **Configuration**: ShadowDragon automatically searches these paths. If you install Tesseract to a custom folder, add `TESSER_EXE=C:\your\custom\path\tesseract.exe` to your `.env` file.

---

### 3. Piper Text-to-Speech Voice Models
Piper TTS synthesizes audio locally using `.onnx` models.
1. Download **BOTH** files of a voice model from the [Piper Voice Samples](https://github.com/rhasspy/piper#samples) (the standard model is `en_US-john-medium`):
   - `.onnx` file (e.g., `en_US-john-medium.onnx`)
   - `.json` config file (e.g., `en_US-john-medium.onnx.json`)
2. Place both downloaded files directly in the `shadowdragon/` package directory (same folder as `main.py`).

---

### 4. Ollama (Required for Offline Fallback)
If you want to run ShadowDragon offline or without a Gemini API Key:
1. **Download**: Download and install [Ollama for Windows](https://ollama.com/download/windows).
2. **Fetch Models**: Open a terminal and pull the fallback routing and agent models:
   ```bash
   ollama pull phi3:mini
   ollama pull mistral
   ```
3. **Keep running**: Ensure the Ollama tray application or server is running in the background.

---

## 🐍 Python Environment & Run Configurations

### 1. Initialize Virtual Environment (Recommended)
Navigate to the project root and create a virtual environment:
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install Dependencies
Install all required libraries (includes PyAudio, OpenAI Whisper, and UI dependencies):
```powershell
pip install -r requirements.txt
```
*(Note: If you run into issues installing `pyaudio` on Windows, download the appropriate precompiled wheel from Christoph Gohlke's unofficial binaries or run `pip install pipwin` followed by `pipwin install pyaudio`.)*

### 3. Configure API Keys
Copy the example environment file:
```powershell
copy .env.example .env
```
Open `.env` in a text editor and enter your Gemini API Key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

---

## 🔍 Verification & Running

### 1. Run Diagnostics
We provide a diagnostics utility to scan for system path configurations and models:
```powershell
python diagnose.py
```
Review the terminal output to ensure FFmpeg, Piper, and python packages are detected.

### 2. Run ShadowDragon
Start the voice assistant with the Desktop Dashboard Control Center:
```powershell
python -m shadowdragon.main
```
If the GUI window successfully renders:
- Status indicators will display **"Waiting for Wake Word..."**.
- Press **Alt + Shift + S** at any time to trigger a voice listening segment manually.
- Voice logs and persistence memory states will display on screen.
