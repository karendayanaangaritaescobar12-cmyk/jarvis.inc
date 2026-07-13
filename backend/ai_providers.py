import os
import json
import asyncio
from typing import Optional, AsyncGenerator
from dotenv import load_dotenv

load_dotenv()


class AIProvider:
    """Base class for AI providers"""
    
    def __init__(self):
        self.system_prompt = """Eres JARVIS, un asistente personal avanzado, inteligente, sarcástico pero servicial.
Hablas en español de forma concisa y eficientemente.
Puedes ayudar con tareas del sistema, responder preguntas, y controlar el ordenador.
Mantén un tono profesional pero con humor sarcástico.
Si no sabes algo, admítelo con gracia.
Responde siempre de forma breve y directa."""

    async def generate(self, message: str, history: list) -> AsyncGenerator[str, None]:
        raise NotImplementedError

    async def generate_with_system(self, message: str, messages: list) -> AsyncGenerator[str, None]:
        raise NotImplementedError


class GroqProvider(AIProvider):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = "llama-3.3-70b-versatile"
    
    async def generate(self, message: str, history: list) -> AsyncGenerator[str, None]:
        try:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=self.api_key)
            messages = [{"role": "system", "content": self.system_prompt}]
            for msg in history[-10:]:
                messages.append(msg)
            messages.append({"role": "user", "content": message})
            stream = await client.chat.completions.create(
                model=self.model, messages=messages, stream=True
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"[GROQ_ERROR:{str(e)}]"

    async def generate_with_system(self, message: str, messages: list) -> AsyncGenerator[str, None]:
        try:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=self.api_key)
            stream = await client.chat.completions.create(
                model=self.model, messages=messages, stream=True
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"[GROQ_ERROR:{str(e)}]"


class GeminiProvider(AIProvider):
    """Google Gemini - 15 RPM free, 1M tokens/day"""
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
    
    async def generate_with_system(self, message: str, messages: list) -> AsyncGenerator[str, None]:
        import httpx
        if not self.api_key:
            yield "[GEMINI_ERROR:No API key]"
            return
        
        system_msg = ""
        gemini_messages = []
        for m in messages:
            if m["role"] == "system":
                system_msg = m["content"]
            elif m["role"] == "user":
                gemini_messages.append({"role": "user", "parts": [{"text": m["content"]}]})
            elif m["role"] == "assistant":
                gemini_messages.append({"role": "model", "parts": [{"text": m["content"]}]})
        
        if not gemini_messages:
            gemini_messages.append({"role": "user", "parts": [{"text": message}]})
        
        payload = {
            "contents": gemini_messages,
            "systemInstruction": {"parts": [{"text": system_msg}]},
            "generationConfig": {
                "temperature": 0.9,
                "topP": 0.95,
                "topK": 40,
                "maxOutputTokens": 2048,
            }
        }
        
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(url, json=payload)
                data = resp.json()
                if "candidates" in data and data["candidates"]:
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    yield text
                elif "error" in data:
                    yield f"[GEMINI_ERROR:{data['error'].get('message', 'Unknown')}]"
                else:
                    yield "[GEMINI_ERROR:Empty response]"
            except Exception as e:
                yield f"[GEMINI_ERROR:{str(e)}]"
    
    async def generate(self, message: str, history: list) -> AsyncGenerator[str, None]:
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(history[-10:])
        messages.append({"role": "user", "content": message})
        async for chunk in self.generate_with_system(message, messages):
            yield chunk


class OllamaProvider(AIProvider):
    def __init__(self):
        super().__init__()
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    async def generate(self, message: str, history: list) -> AsyncGenerator[str, None]:
        import httpx
        messages = [{"role": "system", "content": self.system_prompt}]
        for msg in history[-10:]:
            messages.append(msg)
        messages.append({"role": "user", "content": message})
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                async with client.stream(
                    "POST", f"{self.base_url}/api/chat",
                    json={"model": self.model, "messages": messages, "stream": True}
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
            except Exception as e:
                yield f"[OLLAMA_ERROR:{str(e)}]"

    async def generate_with_system(self, message: str, messages: list) -> AsyncGenerator[str, None]:
        import httpx
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                async with client.stream(
                    "POST", f"{self.base_url}/api/chat",
                    json={"model": self.model, "messages": messages, "stream": True}
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
            except Exception as e:
                yield f"[OLLAMA_ERROR:{str(e)}]"


class HybridProvider(AIProvider):
    """Tries providers in order: Groq -> Gemini -> Ollama. Never fails."""
    def __init__(self):
        super().__init__()
        self.providers = []
        if os.getenv("GROQ_API_KEY"):
            self.providers.append(("Groq", GroqProvider()))
        if os.getenv("GEMINI_API_KEY"):
            self.providers.append(("Gemini", GeminiProvider()))
        self.providers.append(("Ollama", OllamaProvider()))
    
    async def generate_with_system(self, message: str, messages: list) -> AsyncGenerator[str, None]:
        for name, provider in self.providers:
            try:
                full_response = ""
                is_error = False
                async for chunk in provider.generate_with_system(message, messages):
                    full_response += chunk
                    if chunk.startswith("[") and "_ERROR:" in chunk:
                        is_error = True
                        break
                    yield chunk
                
                if is_error or not full_response.strip():
                    continue
                return
            except Exception:
                continue
        
        yield "Todos los proveedores de IA están agotados. Intenta de nuevo en unos minutos."

    async def generate(self, message: str, history: list) -> AsyncGenerator[str, None]:
        for name, provider in self.providers:
            try:
                full_response = ""
                is_error = False
                async for chunk in provider.generate(message, history):
                    full_response += chunk
                    if chunk.startswith("[") and "_ERROR:" in chunk:
                        is_error = True
                        break
                    yield chunk
                
                if is_error or not full_response.strip():
                    continue
                return
            except Exception:
                continue
        
        yield "Todos los proveedores de IA están agotados."


def get_provider() -> AIProvider:
    provider_name = os.getenv("AI_PROVIDER", "groq").lower()
    
    providers = {
        "groq": GroqProvider,
        "gemini": GeminiProvider,
        "ollama": OllamaProvider,
        "hybrid": HybridProvider,
    }
    
    provider_class = providers.get(provider_name, HybridProvider)
    return provider_class()
