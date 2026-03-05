# ShadowDragon Setup Instructions

> [!IMPORTANT]
> **FFmpeg is REQUIRED** for voice detection. If you get a `FileNotFoundError`, it means FFmpeg is missing.

## 1. Local LLMs (Ollama)
... (existing Ollama content) ...

## 2. FFmpeg (REQUIRED)
Whisper cannot "hear" without FFmpeg. **Follow these steps exactly:**
1. **Download**: Go to [gyan.dev](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z) and download the file.
2. **Extract**: Use 7-Zip or WinRAR to extract it to `C:\ffmpeg`.
3. **Add to PATH**:
   - Search for "Environment Variables" in your Start Menu.
   - Click "Environment Variables" button.
   - Under "System Variables", find **Path**, select it, and click **Edit**.
   - Click **New** and paste: `C:\ffmpeg\bin`
   - Click OK on all windows.
4. **Restart**: **You MUST restart your Terminal or VS Code** for this to work.

## 3. Text-to-Speech (Piper)
You can now install Piper via pip:
```bash
pip install piper-tts pathvalidate
```
Then, download **BOTH** the voice model files from the [Piper samples](https://github.com/rhasspy/piper#samples):
1. The `.onnx` file (e.g., `en_US-john-medium.onnx`)
2. The `.json` file (e.g., `en_US-john-medium.onnx.json`)

**Both files must be in the same folder** (put them in the `shadowdragon/` directory).

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
