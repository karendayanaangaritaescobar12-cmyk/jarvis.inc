import json
import os
import datetime
from typing import Dict, List, Optional


class LearningSystem:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.profile_file = os.path.join(self.data_dir, "user_profile.json")
        self.profile = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.profile_file):
            try:
                with open(self.profile_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {
            "name": None,
            "preferences": {},
            "habits": {},
            "expertise_level": "intermediate",
            "interests": [],
            "communication_style": "casual",
            "facts_learned": [],
            "corrections": [],
            "favorite_apps": [],
            "work_schedule": {},
            "location": None,
            "language": "es",
            "last_updated": None
        }

    def _save(self):
        self.profile["last_updated"] = datetime.datetime.now().isoformat()
        with open(self.profile_file, "w", encoding="utf-8") as f:
            json.dump(self.profile, f, ensure_ascii=False, indent=2)

    def learn_from_message(self, user_msg: str, ai_response: str):
        lower = user_msg.lower()

        name_patterns = ["me llamo", "mi nombre es", "soy", "puedes llamarme", "llámame"]
        for pattern in name_patterns:
            if pattern in lower:
                name = lower.split(pattern)[-1].strip().split()[0].title()
                if 1 < len(name) < 20:
                    self.profile["name"] = name
                    self._save()

        pref_patterns = {
            "me gusta": "likes",
            "me encanta": "loves",
            "odio": "dislikes",
            "prefiero": "prefers",
            "siempre uso": "frequent_apps",
            "nunca uso": "avoids"
        }
        for pattern, category in pref_patterns.items():
            if pattern in lower:
                topic = lower.split(pattern)[-1].strip()[:50]
                if topic and len(topic) > 2:
                    if category not in self.profile["preferences"]:
                        self.profile["preferences"][category] = []
                    if topic not in self.profile["preferences"][category]:
                        self.profile["preferences"][category].append(topic)
                        self._save()

        if any(w in lower for w in ["trabajo", "oficina", "reunión", "proyecto", "deadline"]):
            self.profile["habits"]["work_mentioned"] = self.profile["habits"].get("work_mentioned", 0) + 1
        if any(w in lower for w in ["dormir", "acostarse", "despertar", "sueño"]):
            self.profile["habits"]["sleep_mentioned"] = self.profile["habits"].get("sleep_mentioned", 0) + 1
        if any(w in lower for w in ["comer", "almorzar", "cena", "desayuno"]):
            self.profile["habits"]["food_mentioned"] = self.profile["habits"].get("food_mentioned", 0) + 1

        tech_words = ["python", "javascript", "html", "css", "react", "node", "java", "c++",
                       "sql", "git", "docker", "linux", "windows", "api", "rest", "graphql"]
        tech_count = sum(1 for w in tech_words if w in lower)
        if tech_count >= 3:
            self.profile["expertise_level"] = "advanced"
            self._save()
        elif tech_count >= 1:
            self.profile["expertise_level"] = "intermediate"
            self._save()

        if len(ai_response) > 20:
            self.profile["facts_learned"].append({
                "fact": f"Usuario preguntó: {user_msg[:100]}",
                "time": datetime.datetime.now().isoformat()
            })
            if len(self.profile["facts_learned"]) > 200:
                self.profile["facts_learned"] = self.profile["facts_learned"][-200:]
            self._save()

    def get_user_context(self) -> str:
        name = self.profile.get("name") or "desconocido"
        level = self.profile.get("expertise_level", "intermediate")
        prefs = self.profile.get("preferences", {})
        facts = self.profile.get("facts_learned", [])[-5:]

        context = f"Usuario: {name}, nivel: {level}"
        if prefs:
            context += f", preferencias: {json.dumps(prefs, ensure_ascii=False)[:200]}"
        if facts:
            context += f", hechos recientes: {len(facts)}"
        return context

    def get_profile_summary(self) -> str:
        name = self.profile.get("name") or "No identificado"
        level = self.profile.get("expertise_level", "intermediate")
        prefs = self.profile.get("preferences", {})
        facts_count = len(self.profile.get("facts_learned", []))

        summary = f"👤 Perfil del usuario:\n"
        summary += f"• Nombre: {name}\n"
        summary += f"• Nivel técnico: {level}\n"
        summary += f"• Hechos aprendidos: {facts_count}\n"
        if prefs:
            for cat, items in prefs.items():
                summary += f"• {cat}: {', '.join(items[:5])}\n"
        return summary


learning = LearningSystem()
