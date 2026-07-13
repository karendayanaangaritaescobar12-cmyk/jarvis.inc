import time
import json
import os
import asyncio
import datetime
from typing import Optional


class ProactiveEngine:
    """Mark-XLVIII inspired proactive engine with silence detection and LLM-driven suggestions."""

    def __init__(self):
        self.data_file = os.path.join(os.path.dirname(__file__), "data", "proactive_data.json")
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        self.data = self._load_data()
        self.last_user_speech = time.monotonic()
        self._last_triggered = 0
        self.min_silence_secs = 900
        self.check_cooldown = 600
        self.morning_briefing_sent = False
        self.morning_briefing_date = self.data.get("morning_briefing_date")

    def _load_data(self) -> dict:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {"last_triggered": 0, "morning_briefing_date": None}

    def _save_data(self):
        self.data["last_triggered"] = self._last_triggered
        self.data["morning_briefing_date"] = self.morning_briefing_date
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def update_last_speech(self):
        """Call this every time the user speaks."""
        self.last_user_speech = time.monotonic()

    def should_trigger(self) -> bool:
        """Check if we should proactively reach out."""
        now = time.monotonic()
        silence = now - self.last_user_speech
        gap = now - self._last_triggered
        return silence >= self.min_silence_secs and gap >= self.check_cooldown

    def build_prompt(self, memory: dict, monitor_context: str = "") -> str:
        """Build a prompt for the AI to decide what proactive message to send."""
        now = datetime.datetime.now()
        hour = now.hour
        name = memory.get("user_name", "señor")
        convos = memory.get("total_messages", 0)
        topics = memory.get("topics_discussed", {})
        top_topic = max(topics, key=topics.get) if topics else "general"

        prompt = f"""[PROACTIVE_CHECK]
Hora actual: {now.strftime('%H:%M')}
Nombre del usuario: {name}
Conversaciones totales: {convos}
Tema principal: {top_topic}
Contexto del sistema: {monitor_context or 'Normal'}
Tiempo sin hablar: {int((time.monotonic() - self.last_user_speech) / 60)} minutos

Eres JARVIS. El usuario lleva tiempo sin hablar. Decide si debes enviarle un mensaje proactivo.
Solo envia algo si es relevante y natural. No fuerces la conversacion.

Posibles acciones:
1. Si es hora de almuerzo (12-14h): sugiere una pausa
2. Si es tarde (>23h): sugiere descansar
3. Si el sistema tiene anomalias: notificar
4. Si puedes anticipar algo util: hacerlo
5. Si no hay nada relevante: responde SOLO con "IGNORAR"

Responde SOLO con el mensaje que JARVIS le enviaria al usuario, o "IGNORAR" si no hay nada relevante."""
        return prompt

    def should_send_morning_briefing(self) -> bool:
        """Check if we should send a morning briefing today."""
        today = datetime.date.today().isoformat()
        if self.morning_briefing_date == today:
            return False
        hour = datetime.datetime.now().hour
        return 6 <= hour <= 9

    def build_morning_briefing_prompt(self, memory: dict, weather: str = "", news: str = "") -> str:
        """Build a prompt for the AI to generate a morning briefing."""
        name = memory.get("user_name", "señor")
        now = datetime.datetime.now()

        prompt = f"""[MORNING_BRIEFING]
Eres JARVIS. Genera un saludo matutino para {name}.
Hora: {now.strftime('%H:%M')}
Fecha: {now.strftime('%A %d de %B de %Y')}

Incluye:
- Saludo personalizado basado en la hora y dia de la semana
- Resumen del clima si esta disponible
- Noticias destacadas si estan disponibles
- Un recordatorio breve de productividad o motivacion
- Mantenlo breve (3-5 lineas)
- Incluye tu sarcasmo caracteristico"""
        return prompt

    def mark_morning_briefing_sent(self):
        """Mark that we sent the morning briefing today."""
        self.morning_briefing_date = datetime.date.today().isoformat()
        self._save_data()

    def mark_triggered(self):
        """Mark that we just triggered a proactive check."""
        self._last_triggered = time.monotonic()
        self._save_data()


proactive_engine = ProactiveEngine()
