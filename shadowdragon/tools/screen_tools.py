import pyautogui
import pytesseract
from shadowdragon.config import TESSER_EXE

pytesseract.pytesseract.tesseract_cmd = TESSER_EXE

class ScreenTools:
    def capture_screen(self, filename="screenshot.png"):
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return filename

    def read_screen(self):
        filename = self.capture_screen()
        text = pytesseract.image_to_string(filename)
        return text

    def analyze_screen(self, query, agent):
        text = self.read_screen()
        prompt = f"The user asked: '{query}'. Based on the text extracted from the screen below, provide an answer.\n\nExtracted Text:\n{text}"
        return agent.ask(prompt)
