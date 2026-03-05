# ShadowDragon Setup Instructions

> [!IMPORTANT]
> **FFmpeg is REQUIRED** for voice detection. If you get a `FileNotFoundError`, it means FFmpeg is missing.

## 1. Local LLMs (Ollama)
... (existing Ollama content) ...

## 2. FFmpeg (Required for Voice)
ShadowDragon needs FFmpeg to process audio.
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html) or [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
2. Extract and add the `bin` folder to your **System PATH**.
3. **Restart your computer** after adding it to PATH.
4. Verify by running `ffmpeg -version` in a terminal.

## 3. Text-to-Speech (Piper)
You can now install Piper via pip:
```bash
pip install piper-tts
```
Then, download a voice model (`.onnx` file) from the [Piper samples](https://github.com/rhasspy/piper#samples).
Place the model (e.g., `en_GB-alan-low.onnx`) in the `shadowdragon/` directory, or update `PIPER_MODEL` in `config.py`.

## 3. OCR (Tesseract)
Install [Tesseract OCR for Windows](https://github.com/UB-Mannheim/tesseract/wiki).
Update the path in `shadowdragon/config.py` if different from `C:\Program Files\Tesseract-OCR\tesseract.exe`.

## 4. Python Dependencies
```bash
pip install -r requirements.txt
```

## 5. Run ShadowDragon
```bash
python -m shadowdragon.main
```
