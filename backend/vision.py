import os
import base64
import tempfile
from typing import Optional


class VisionModule:
    def __init__(self):
        self.screenshot_dir = os.path.join(os.path.dirname(__file__), "data", "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)

    async def take_screenshot(self) -> Optional[str]:
        try:
            import pyautogui
            timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.screenshot_dir, f"screenshot_{timestamp}.png")
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            return filepath
        except Exception as e:
            return None

    async def analyze_screenshot(self, ai_provider=None) -> str:
        filepath = await self.take_screenshot()
        if not filepath:
            return "No pude tomar la captura de pantalla."

        try:
            with open(filepath, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()

            if ai_provider:
                prompt = "Describe brevemente lo que ves en esta captura de pantalla. ¿Qué aplicaciones están abiertas? ¿Qué hay visible?"
                return f"📸 Captura guardada en: {filepath}\n\nAnálisis: No tengo visión habilitada aún, pero la captura está guardada."

            return f"📸 Captura guardada en: {filepath}"
        except Exception as e:
            return f"Error con la captura: {str(e)[:100]}"

    def list_screenshots(self) -> str:
        files = [f for f in os.listdir(self.screenshot_dir) if f.endswith('.png')]
        if not files:
            return "No hay capturas guardadas."
        result = f"📸 {len(files)} capturas:\n"
        for f in sorted(files, reverse=True)[:10]:
            size = os.path.getsize(os.path.join(self.screenshot_dir, f))
            result += f"• {f} ({size // 1024}KB)\n"
        return result

    def cleanup_old(self, max_keep: int = 20):
        files = sorted([f for f in os.listdir(self.screenshot_dir) if f.endswith('.png')])
        if len(files) > max_keep:
            for f in files[:len(files) - max_keep]:
                os.remove(os.path.join(self.screenshot_dir, f))


vision = VisionModule()
