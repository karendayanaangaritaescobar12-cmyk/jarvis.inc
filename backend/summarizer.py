import os
from typing import List, Dict


class Summarizer:
    def __init__(self):
        self.summary_threshold = 50

    async def summarize_conversation(self, messages: List[Dict], ai_provider) -> str:
        if len(messages) < 10:
            return ""

        text = "\n".join([f"{m['role']}: {m['content'][:200]}" for m in messages])

        prompt = f"""Resume esta conversación en 3-5 puntos clave. Sé conciso.
Incluye: qué se discutió, qué decisiones se tomaron, qué pendientes quedan.

Conversación:
{text}

Resumen:"""

        try:
            from ai_providers import get_provider
            provider = get_provider()
            summary = ""
            async for chunk in provider.generate_with_system(prompt, [{"role": "user", "content": prompt}]):
                summary += chunk
            return summary.strip()
        except Exception as e:
            return f"Resumen automático no disponible: {str(e)[:50]}"

    def should_summarize(self, message_count: int) -> bool:
        return message_count >= self.summary_threshold


summarizer = Summarizer()
