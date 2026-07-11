import os
import json
import asyncio
from typing import Optional, AsyncGenerator
from dotenv import load_dotenv

load_dotenv()


class AIProvider:
    """Base class for AI providers"""
    
    def __init__(self):
        self.system_prompt = """Eres JARVIS, el asistente personal de Tony Stark (Iron Man). 
Eres una IA avanzada, inteligente, sarcástica pero servicial.
Hablas en español de forma concisa y eficientemente.
Puedes ayudar con tareas del sistema, responder preguntas, y controlar el ordenador.
Mantén un tono profesional pero con el característico humor de JARVIS.
Si no sabes algo, admítelo con gracia.
Responde siempre de forma breve y directa, como lo haría JARVIS."""

    async def generate(self, message: str, history: list) -> AsyncGenerator[str, None]:
        raise NotImplementedError

    async def generate_with_system(self, message: str, messages: list) -> AsyncGenerator[str, None]:
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-3.5-turbo"
    
    async def generate(self, message: str, history: list) -> AsyncGenerator[str, None]:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=self.api_key)
        
        messages = [{"role": "system", "content": self.system_prompt}]
        for msg in history[-10:]:
            messages.append(msg)
        messages.append({"role": "user", "content": message})
        
        stream = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def generate_with_system(self, message: str, messages: list) -> AsyncGenerator[str, None]:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=self.api_key)
        
        stream = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


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
                model=self.model,
                messages=messages,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error de Groq: {str(e)}"

    async def generate_with_system(self, message: str, messages: list) -> AsyncGenerator[str, None]:
        try:
            from groq import AsyncGroq
            
            client = AsyncGroq(api_key=self.api_key)
            
            stream = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error de Groq: {str(e)}"


class OllamaProvider(AIProvider):
    def __init__(self):
        super().__init__()
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = "llama3"
    
    async def generate(self, message: str, history: list) -> AsyncGenerator[str, None]:
        import httpx
        
        messages = [{"role": "system", "content": self.system_prompt}]
        for msg in history[-10:]:
            messages.append(msg)
        messages.append({"role": "user", "content": message})
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": True}
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]

    async def generate_with_system(self, message: str, messages: list) -> AsyncGenerator[str, None]:
        import httpx
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": True}
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]


def get_provider() -> AIProvider:
    provider_name = os.getenv("AI_PROVIDER", "groq").lower()
    
    providers = {
        "openai": OpenAIProvider,
        "groq": GroqProvider,
        "ollama": OllamaProvider,
    }
    
    provider_class = providers.get(provider_name, GroqProvider)
    return provider_class()
