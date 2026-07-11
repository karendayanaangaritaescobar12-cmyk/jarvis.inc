import os
import asyncio
from typing import Optional


class VoiceManager:
    """Voice manager - TTS is handled by the browser, this is a stub for API compatibility."""
    
    def __init__(self):
        self.is_listening = False
    
    async def listen(self) -> Optional[str]:
        """Voice recognition is handled by the browser Web Speech API"""
        return None
    
    def speak(self, text: str):
        """TTS is handled by the browser"""
        pass
    
    async def speak_async(self, text: str):
        """TTS is handled by the browser"""
        pass


voice_manager = VoiceManager()
