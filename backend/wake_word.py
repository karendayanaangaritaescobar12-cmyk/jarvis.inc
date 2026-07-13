import re
from typing import Optional


class WakeWordDetector:
    def __init__(self):
        self.wake_words = [
            "oye jarvis", "hey jarvis", "hola jarvis", "buenas jarvis",
            "escucha jarvis", "jarvis", "asistente",
            "oye ia", "hey ia", "hola ia",
        ]
        self.is_listening = False
        self.timeout_seconds = 10

    def detect(self, text: str) -> bool:
        if not text:
            return False
        lower = text.lower().strip()
        for wake in self.wake_words:
            if lower.startswith(wake):
                return True
        return False

    def extract_command(self, text: str) -> Optional[str]:
        if not text:
            return None
        lower = text.lower().strip()
        for wake in self.wake_words:
            if lower.startswith(wake):
                command = lower[len(wake):].strip()
                if command:
                    return command.lstrip(",:;. ")
        return None

    def is_wake_word_only(self, text: str) -> bool:
        return self.extract_command(text) is None and self.detect(text)


wake_detector = WakeWordDetector()
