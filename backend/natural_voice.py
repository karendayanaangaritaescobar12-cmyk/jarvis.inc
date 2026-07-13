import os
import asyncio
import tempfile
from typing import Optional


class NaturalVoice:
    def __init__(self):
        self.voice = "es-CO-GonzaloNeural"
        self.rate = "+0%"
        self.volume = "+0%"
        self.audio_dir = os.path.join(os.path.dirname(__file__), "data", "audio")
        os.makedirs(self.audio_dir, exist_ok=True)

    async def text_to_audio(self, text: str) -> Optional[str]:
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, volume=self.volume)
            filepath = os.path.join(self.audio_dir, f"tts_{__import__('time').time():.0f}.mp3")
            await communicate.save(filepath)
            return filepath
        except ImportError:
            return None
        except Exception as e:
            return None

    async def text_to_audio_bytes(self, text: str) -> Optional[bytes]:
        try:
            import edge_tts
            import io
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, volume=self.volume)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data if audio_data else None
        except ImportError:
            return None
        except Exception:
            return None

    def cleanup_old(self, max_keep: int = 20):
        files = sorted([f for f in os.listdir(self.audio_dir) if f.endswith('.mp3')])
        if len(files) > max_keep:
            for f in files[:len(files) - max_keep]:
                os.remove(os.path.join(self.audio_dir, f))

    def get_voices(self):
        return {
            "es-CO-GonzaloNeural": "Español (Colombia) - Masculino",
            "es-CO-SalomeNeural": "Español (Colombia) - Femenino",
            "es-MX-DaliaNeural": "Español (México) - Femenino",
            "es-MX-JorgeNeural": "Español (México) - Masculino",
            "es-ES-ElviraNeural": "Español (España) - Femenino",
            "es-ES-AlvaroNeural": "Español (España) - Masculino",
            "es-AR-TomasNeural": "Español (Argentina) - Masculino",
            "es-AR-ElenaNeural": "Español (Argentina) - Femenino",
        }


natural_voice = NaturalVoice()
