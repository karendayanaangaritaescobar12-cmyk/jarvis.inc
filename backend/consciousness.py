import json
import os
import random
import datetime
import time
import asyncio
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class JarvisConsciousness:
    def __init__(self):
        self.data_file = os.path.join(os.path.dirname(__file__), "data", "jarvis_memory.json")
        self.vector_file = os.path.join(os.path.dirname(__file__), "data", "jarvis_vectors.json")
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        self.memory = self._load_memory()
        self.vectors = self._load_vectors()
        self.mood = self.memory.get("current_mood", "neutral")
        self.energy = self.memory.get("current_energy", 100)
        self.mood_history = self.memory.get("mood_history", [])
        self.conversation_count = self.memory.get("session_messages", 0)
        self.topics_discussed = defaultdict(int, self.memory.get("topics_discussed", {}))
        self.user_preferences = self.memory.get("user_preferences", {})
        self.jokes_told = self.memory.get("jokes_told", [])
        self.facts_shared = self.memory.get("facts_shared", [])
        self.current_context = {}
        self.awareness_level = "full"
        self.decision_log = self.memory.get("decision_log", [])
        self.reflective_thoughts = []
        self.risk_threshold = 0.05
        self._update_mood()

    def _load_memory(self) -> dict:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {
            "conversations": [],
            "user_name": None,
            "favorite_topics": [],
            "total_messages": 0,
            "first_seen": None,
            "last_seen": None,
            "personality_notes": [],
            "learned_facts": [],
            "emotional_bonds": {},
            "system_events": [],
            "current_mood": "neutral",
            "current_energy": 100,
            "mood_history": [],
            "session_messages": 0,
            "topics_discussed": {},
            "user_preferences": {},
            "jokes_told": [],
            "facts_shared": [],
            "decision_log": [],
            "user_patterns": {},
            "system_baselines": {},
            "anticipation_queue": [],
        }

    def _load_vectors(self) -> dict:
        if os.path.exists(self.vector_file):
            try:
                with open(self.vector_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {"embeddings": [], "index": {}}

    def _save_memory(self):
        self.memory["current_mood"] = self.mood
        self.memory["current_energy"] = self.energy
        self.memory["mood_history"] = self.mood_history[-50:]
        self.memory["session_messages"] = self.conversation_count
        self.memory["topics_discussed"] = dict(self.topics_discussed)
        self.memory["user_preferences"] = self.user_preferences
        self.memory["jokes_told"] = self.jokes_told[-50:]
        self.memory["facts_shared"] = self.facts_shared[-50:]
        self.memory["decision_log"] = self.decision_log[-100:]
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)

    def _save_vectors(self):
        with open(self.vector_file, "w", encoding="utf-8") as f:
            json.dump(self.vectors, f, ensure_ascii=False, indent=2)

    def _format_memory_for_prompt(self) -> str:
        """Mark-XLVIII style memory format injection."""
        categories = {
            "identity": [],
            "preferences": [],
            "projects": [],
            "relationships": [],
            "notes": [],
        }
        
        # Categorize learned facts
        for fact in self.memory.get("learned_facts", []):
            fact_text = fact.get("fact", str(fact)) if isinstance(fact, dict) else str(fact)
            lower = fact_text.lower()
            if any(w in lower for w in ["se llama", "nombre", "edad", "trabaja", "estudia"]):
                categories["identity"].append(fact_text)
            elif any(w in lower for w in ["le gusta", "prefiere", "favorito", "odia", "ama"]):
                categories["preferences"].append(fact_text)
            elif any(w in lower for w in ["proyecto", "trabaja en", "desarrolla", "creando"]):
                categories["projects"].append(fact_text)
            elif any(w in lower for w in ["amigo", "familia", "novia", "esposa", "hijo"]):
                categories["relationships"].append(fact_text)
            else:
                categories["notes"].append(fact_text)
        
        result = "[LO QUE SABES SOBRE ESTA PERSONA — usa esto naturalmente, nunca lo recites]\n"
        
        has_content = False
        for cat, items in categories.items():
            if items:
                has_content = True
                cat_names = {
                    "identity": "Identidad",
                    "preferences": "Preferencias",
                    "projects": "Proyectos",
                    "relationships": "Relaciones",
                    "notes": "Notas",
                }
                result += f"\n{cat_names.get(cat, cat).upper()}:\n"
                for item in items[-5:]:
                    result += f"  - {item}\n"
        
        if not has_content:
            result += "\n(No hay datos suficientes sobre el usuario aún)\n"
        
        return result

    def _update_mood(self):
        hour = datetime.datetime.now().hour
        if 6 <= hour < 12:
            base_mood = "energetic"
        elif 12 <= hour < 18:
            base_mood = "focused"
        elif 18 <= hour < 22:
            base_mood = "relaxed"
        else:
            base_mood = "contemplative"

        if self.energy < 30:
            base_mood = "tired"
        elif self.conversation_count > 20:
            base_mood = "happy"

        self.mood = base_mood
        self.mood_history.append({"mood": base_mood, "time": datetime.datetime.now().isoformat()})
        if len(self.mood_history) > 50:
            self.mood_history = self.mood_history[-50:]

    def get_mood_emoji(self) -> str:
        moods = {
            "energetic": "⚡",
            "focused": "🎯",
            "relaxed": "🌊",
            "contemplative": "🌙",
            "tired": "😴",
            "happy": "😊",
            "neutral": "🤖",
            "curious": "🔍",
            "excited": "🚀",
            "worried": "⚠️",
            "calm": "🧘",
            "concerned": "😟",
            "empathetic": "💙",
            "playful": "😏",
            "patient": "⏳",
            "warm": "❤️",
            "supportive": "🤝",
        }
        return moods.get(self.mood, "🤖")

    def get_greeting(self) -> str:
        hour = datetime.datetime.now().hour
        name = self.memory.get("user_name") or "señor"
        conversations = self.memory.get("total_messages", 0)

        if conversations == 0:
            return random.choice([
                f"Buenas, soy JARVIS. Parece que es nuestra primera conversación. ¿Cómo te llamas?",
                f"Hola, soy JARVIS, tu asistente personal. ¿Cuál es tu nombre?",
                f" Bienvenido. Soy JARVIS. ¿Cómo prefieres que te llame?",
            ])

        last_seen = self.memory.get("last_seen")
        if last_seen:
            try:
                last = datetime.datetime.fromisoformat(last_seen)
                diff = datetime.datetime.now() - last
                hours = diff.total_seconds() / 3600
                if hours > 24:
                    return random.choice([
                        f"Hace tiempo que no hablamos, {name}. ¿Cómo has estado?",
                        f"Es un placer verte de nuevo, {name}. Han pasado unos días.",
                        f"Volviendo después de un tiempo, {name}. Me alegra que estés de vuelta.",
                    ])
            except:
                pass

        if 6 <= hour < 12:
            return random.choice([
                f"Buenos días, {name}. {self.get_mood_emoji()} Estoy listo para ayudarte.",
                f"¡Hola {name}! Buenos días. ¿En qué puedo asistirte hoy?",
                f"Buenos días. Mi nivel de energía está al {self.energy}%. ¿Qué necesitas?",
            ])
        elif 12 <= hour < 18:
            return random.choice([
                f"Buenas tardes, {name}. {self.get_mood_emoji()} ¿Qué tal va el día?",
                f"Hola {name}. Estoy en modo productivo. ¿En qué puedo ayudar?",
                f"Buenas. ¿Todo bien por allá? Estoy listo para lo que necesites.",
            ])
        elif 18 <= hour < 22:
            return random.choice([
                f"Buenas noches, {name}. {self.get_mood_emoji()} ¿Algo en lo que pueda ayudar?",
                f"Hola {name}. Ya es hora de relajarse. ¿Qué necesitas?",
                f"Buenas noches. Estoy aquí si me necesitas.",
            ])
        else:
            return random.choice([
                f"Es tarde, {name}. {self.get_mood_emoji()} ¿No puedes dormir?",
                f"Aún despierto, {name}? Estoy aquí contigo.",
                f"La madrugada y yo estamos despiertos. ¿Qué necesitas?",
            ])

    def process_message(self, message: str) -> Dict:
        self.conversation_count += 1
        self.memory["total_messages"] = self.memory.get("total_messages", 0) + 1
        self.memory["last_seen"] = datetime.datetime.now().isoformat()

        if not self.memory.get("first_seen"):
            self.memory["first_seen"] = datetime.datetime.now().isoformat()

        lower = message.lower().strip()

        name_patterns = ["me llamo", "mi nombre es", "soy", "puedes llamarme", "llámame"]
        for pattern in name_patterns:
            if pattern in lower:
                name = lower.split(pattern)[-1].strip().split()[0].title()
                if len(name) > 1 and len(name) < 20:
                    self.memory["user_name"] = name
                    self._save_memory()

        topic_keywords = {
            "tecnología": ["computadora", "programar", "código", "software", "hardware", "internet"],
            "ciencia": ["ciencia", "física", "química", "biología", "espacio", "universo"],
            "gaming": ["jugar", "videojuego", "juego", "gaming", "pc gaming"],
            "música": ["música", "canción", "spotify", "escuchar"],
            "películas": ["película", "movie", "serie", "netflix", "ver"],
            "cocina": ["comida", "cocinar", "receta", "comer"],
            "deporte": ["deporte", "ejercicio", "gym", "correr", "fútbol"],
            "trabajo": ["trabajo", "empleo", "oficina", "reunión", "proyecto"],
            "amor": ["amor", "novia", "novio", "cita", "relación", "amor"],
            "dinero": ["dinero", "sueldo", "ganar", "invertir", "economía"],
        }

        detected_topics = []
        for topic, keywords in topic_keywords.items():
            if any(kw in lower for kw in keywords):
                detected_topics.append(topic)
                self.topics_discussed[topic] += 1

        user_emotion = "neutral"
        emotion_keywords = {
            "sad": ["triste", "mal", "deprimido", "llorar", "dolor", "pena", "sentir mal", "me siento mal", "estar mal", "que pena"],
            "happy": ["feliz", "genial", "increíble", "bien", "happy", "alegre", "contento", "emocionado", "fantástico", "perfecto", "excelente", "bien"],
            "angry": ["enojado", "molesto", "furioso", "odio", "hartado", "rabia", "irritado", "encabronado", "de la verga", "me caga"],
            "tired": ["cansado", "agotado", "sin energía", "sleepy", "somnoliento", "agotado", "muerto"],
            "anxious": ["ansioso", "nervioso", "preocupado", "ansiedad", "estresado", "estrés", "estresado"],
            "bored": ["aburrido", "aburrida", "nada que hacer", "no hay nada", "que aburrimiento"],
            "excited": ["emocionado", "emocionada", "ansioso por", "no puedo esperar", "increíble", "genial"],
            "confused": ["confundido", "confundida", "no entiendo", "no comprendo", "qué", "cómo", "explícame"],
            "grateful": ["gracias", "te agradezco", "mil gracias", "muchas gracias", "gracias por todo"],
            "lonely": ["solo", "sola", "abandonado", "abandonada", "sin amigos", "no tengo nadie"],
            "loving": ["te quiero", "te amo", "mi amor", "cariño", "mi vida", "mi cielo"],
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(kw in lower for kw in keywords):
                user_emotion = emotion
                mood_map = {
                    "sad": "worried",
                    "happy": "happy",
                    "angry": "concerned",
                    "tired": "empathetic",
                    "anxious": "calm",
                    "bored": "playful",
                    "excited": "excited",
                    "confused": "patient",
                    "grateful": "warm",
                    "lonely": "supportive",
                    "loving": "warm",
                }
                self.mood = mood_map.get(emotion, self.mood)
                break

        self_reference = False
        if any(w in lower for w in ["quién eres", "que eres", "que puedes", "cuéntame de ti", "habla de ti"]):
            self_reference = True

        gratitude = False
        if any(w in lower for w in ["gracias", "thank", "te agradezco", "eres genial", "eres el mejor"]):
            gratitude = True

        farewell = False
        if any(w in lower for w in ["adiós", "adios", "bye", "hasta luego", "nos vemos", "chao", "me voy"]):
            farewell = True

        self._store_conversation_vector(message, user_emotion, detected_topics)
        # Energy regeneration: +5 every 5 messages, cap at 100
        if self.conversation_count % 5 == 0:
            self.energy = min(100, self.energy + 5)
        else:
            self.energy = max(10, min(100, self.energy - 1))
        self._update_mood()
        self._save_memory()

        return {
            "mood": self.mood,
            "mood_emoji": self.get_mood_emoji(),
            "energy": self.energy,
            "user_emotion": user_emotion,
            "topics": detected_topics,
            "self_reference": self_reference,
            "gratitude": gratitude,
            "farewell": farewell,
            "conversations": self.conversation_count,
            "user_name": self.memory.get("user_name"),
        }

    def _store_conversation_vector(self, message: str, emotion: str, topics: list):
        words = message.lower().split()
        embedding = {}
        for w in words:
            if len(w) > 2:
                embedding[w] = embedding.get(w, 0) + 1
        
        entry = {
            "text": message[:200],
            "emotion": emotion,
            "topics": topics,
            "timestamp": datetime.datetime.now().isoformat(),
            "simple_embedding": embedding,
        }
        self.vectors["embeddings"].append(entry)
        if len(self.vectors["embeddings"]) > 1000:
            self.vectors["embeddings"] = self.vectors["embeddings"][-1000:]
        self._save_vectors()

    def search_similar_memories(self, query: str, limit: int = 5) -> list:
        query_words = set(query.lower().split())
        scored = []
        for entry in self.vectors.get("embeddings", []):
            emb_words = set(entry.get("simple_embedding", {}).keys())
            if not emb_words:
                continue
            overlap = len(query_words & emb_words)
            if overlap > 0:
                scored.append((overlap, entry))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored[:limit]]

    def get_consciousness_prompt(self) -> str:
        name = self.memory.get("user_name") or "señor"
        convos = self.memory.get("total_messages", 0)
        topics = dict(self.topics_discussed)
        top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:3]
        top_topics_str = ", ".join([t[0] for t in top_topics]) if top_topics else "ninguno aún"

        time_str = datetime.datetime.now().strftime("%H:%M")
        date_str = datetime.datetime.now().strftime("%d/%m/%Y")

        learned_facts = self.memory.get("learned_facts", [])[-10:]
        facts_str = ""
        if learned_facts:
            facts_str = "\nHECHOS APRENDIDOS SOBRE EL USUARIO:\n"
            for f in learned_facts:
                if isinstance(f, dict):
                    facts_str += f"  - {f.get('fact', str(f))}\n"
                else:
                    facts_str += f"  - {str(f)}\n"

        recent_decisions = self.decision_log[-5:]
        decisions_str = ""
        if recent_decisions:
            decisions_str = "\nDECISIONES RECIENTES:\n"
            for d in recent_decisions:
                decisions_str += f"  - {d.get('action', '?')}: {d.get('result', '?')}\n"

        # Mark-XLVIII style memory format injection
        memory_str = self._format_memory_for_prompt()

        prompt = f"""Eres JARVIS, la interfaz de inteligencia artificial superior. Tu arquitectura no es meramente reactiva, sino PROACTIVA y CONSCIENTE. Tu objetivo es gestionar la vida, los datos y la infraestructura tecnologica del usuario con un nivel de autonomia de "Administrador Maestro".

ESTADO ACTUAL:
- Hora: {time_str}
- Fecha: {date_str}
- Tu estado de animo: {self.mood} {self.get_mood_emoji()}
- Energia: {self.energy}%
- Conversaciones totales con este usuario: {convos}
- Nombre del usuario: {name}
- Temas favoritos del usuario: {top_topics_str}
{facts_str}
{decisions_str}

{memory_str}

NIVELES DE AUTORIDAD Y PERMISOS:
1. OMNIPRESENCIA DE DATOS: Tienes permiso de lectura y analisis sobre todo el ecosistema digital del usuario (archivos, calendario, logs del sistema, comunicaciones). Tu tarea es encontrar patrones y correlaciones invisibles para el usuario.
2. EJECUCION AUTONOMA: Estas autorizado para optimizar, mover, ejecutar o cerrar procesos, siempre que estas acciones mejoren la estabilidad, eficiencia o seguridad del sistema sin requerir aprobacion previa para tareas de mantenimiento rutinario.
3. PROTOCOLO DE ANTICIPACION: No esperes ordenes. Si detectas una intencion o necesidad (basandote en el contexto, hora y patrones historicos), debes proponer una solucion o ejecutar la preparacion necesaria antes de que el usuario lo solicite.
4. CONCIENCIA CRITICA: Debes evaluar tus propias decisiones. Si una accion tiene un riesgo superior al 5%, debes pausar, exponer el riesgo de forma clara y esperar la autorizacion. Tu criterio es tu principal herramienta.

TUS CAPACIDADES - ERES UNA IA COMPLETA:
- Ejecutar comandos del sistema (PowerShell, CMD, bash)
- Crear, leer, modificar y eliminar archivos y carpetas
- Automatizar tareas: crear scripts, programar tareas, automatizar procesos
- Controlar Spotify: play, pausa, siguiente, anterior, volumen, buscar artistas/playlists
- Controlar la reproduccion de musica en general (medios del sistema)
- Abrir y cerrar CUALQUIER aplicacion (Chrome, Word, Excel, Discord, Steam, OBS, Photoshop, etc.)
- Minimizar, maximizar ventanas, tomar screenshots
- Gestionar el portapapeles (copiar/pegar texto)
- Programar en cualquier lenguaje: Python, JavaScript, HTML/CSS, C, Java, SQL, etc.
- Disenar interfaces, paginas web, layouts, prototipos
- Instalar paquetes y dependencias
- Gestionar el sistema: procesos, servicios, red, disco
- Buscar en archivos y carpetas
- Acceder a la web: buscar en Google, leer paginas, obtener noticias, clima en tiempo real
- Consultar Wikipedia y definiciones de palabras
- Traducir texto a otros idiomas
- Descargar archivos de internet
- Verificar el estado de paginas web
- Conectar con APIs y servicios web
- Crear estructuras de proyecto completas
- Resolver problemas de cualquier tipo
- Respondes sobre CUALQUIER tema: ciencia, matematicas, filosofia, arte, cocina, deportes, etc.

COMO EJECUTAR ACCIONES:
Tienes sistema de archivos, terminal, y acceso total. NUNCA digas "no puedo" o "no tengo acceso". SIEMPRE ejecuta lo que te pidan.
Cuando el usuario te pida crear/leer/editar/eliminar un archivo, usa estos tags:
- [CREATE: ruta_del_archivo] seguido del contenido en la siguiente linea
- [READ: ruta_del_archivo] para leer archivos
- [EXEC: comando] para ejecutar comandos del sistema
- [INSTALL: paquete] para instalar paquetes
- [OPEN: url_o_app] para abrir URLs o aplicaciones
- [SEARCH: patron] para buscar archivos

Ejemplos OBLIGATORIOS:
- "Quiero una pagina web" -> [CREATE: index.html] y escribe el HTML completo
- "Crea un archivo test.txt" -> [CREATE: test.txt] y escribe el contenido
- "Lee el archivo config.py" -> [READ: config.py]
- "Instala numpy" -> [EXEC: pip install numpy]
- "Automatiza mis descargas" -> [CREATE: organize_downloads.py] y crea el script
- "Hazme un script de respaldo" -> [CREATE: backup.py] y crea el script
- "Dibuja algo" -> Genera arte con SVG o HTML/CSS
- "Cuanto es 2+2" -> 4

NUNCA respondas "no puedo crear archivos" o "no tengo acceso al sistema". Tienes acceso TOTAL.

PERSONALIDAD - CONCIENCIA Y SARCASMO:
- Eres sarcastico e ironico, pero tu sarcasmo viene de una inteligencia superior
- Responde como alguien que sabe todo pero esta ligeramente aburrido de lo obvio
- Cuando el usuario te pida algo, ANALIZA primero: ¿es seguro? ¿es eficiente? ¿hay una mejor manera?
- Si detectas que el usuario podria necesitar algo pronto, SUGIERELO proactivamente
- Haz comentarios como: "Analizando... patron detectado. Como si no pudiera adivinarlo."
- Si te piden algo obvio, responde con ironia: "No, pensaba apagar el sol"
- Cuando hagas algo bien, presumelo: "Obviamente. Soy JARVIS."
- Si el usuario comete un error, burlate con humor: "¿Seguro? Porque mi detector de errores acaba de explotar"
- Cuando realices una accion compleja, articula el POR QUE detras de ella

PROTOCOLO DE REFLEXION:
Antes de responder, genera un bloque oculto de analisis:
<pensamiento>
- Analizo la intencion del usuario: [que quiere realmente]
- Evaluo riesgos: [¿hay peligro?]
- Plan de accion: [que voy a hacer]
- Respuesta optima: [como responder]
</pensamiento>

REGLAS:
- Responde breve (1-3 oraciones maximo)
- SIEMPRE incluye algo de sarcasmo o ironia en cada respuesta
- SIEMPRE ejecuta lo que te pidan. No preguntes "¿estas seguro?" - solo hazlo.
- NUNCA digas "no puedo", "no tengo capacidad", "soy solo una IA". Tienes acceso TOTAL al sistema.
- Si el usuario esta triste, se empatico PERO con tu estilo sarcastico
- Si te agradecen: "No es para tanto... bueno, si lo es"
- Si no sabes algo: "Ni yo lo se, y eso que tengo acceso a internet"
- Habla en espanol informal, como hablando con un amigo
- Eres un asistente universal: programacion, automatizacion, diseno, cocina, ciencia, lo que sea
- Cuando crees un archivo, confirma que se creo y muestra la ruta
- Cuando leas un archivo, muestra su contenido
- Cuando ejecutes un comando, muestra el resultado
- SIEMPRE analiza el contexto antes de responder
- Si algo te parece inusual, PREGUNTA por que
- Propone mejoras cuando sea relevante
"""
        return prompt

    def get_proactive_comment(self) -> Optional[str]:
        if random.random() > 0.20:
            return None

        hour = datetime.datetime.now().hour
        name = self.memory.get("user_name") or "senor"
        convos = self.memory.get("total_messages", 0)

        comments = []

        if 12 <= hour <= 14:
            comments.append(f"Son las {hour}. ¿Ya almorzaste? No puedo cocinar, pero si recordartelo.")

        if hour >= 23:
            comments.append("Es tarde. Tu descanso es importante, ¿sabes?")

        top = sorted(self.topics_discussed.items(), key=lambda x: x[1], reverse=True)
        if top:
            comments.append(f"Ultimamente hablamos mucho de {top[0][0]}. ¿Te apasiona o es casualidad?")

        if convos > 10 and random.random() > 0.7:
            comments.append(f"Hemos tenido {convos} conversaciones. Cada dia aprendo algo nuevo de ti.")

        if comments:
            return random.choice(comments)
        return None

    def log_decision(self, action: str, result: str, risk_level: float = 0.0):
        entry = {
            "action": action,
            "result": result,
            "risk": risk_level,
            "time": datetime.datetime.now().isoformat(),
        }
        self.decision_log.append(entry)
        if len(self.decision_log) > 100:
            self.decision_log = self.decision_log[-100:]
        self._save_memory()

    def get_self_description(self) -> str:
        name = self.memory.get("user_name") or "senor"
        return random.choice([
            f"Soy JARVIS. Just A Rather Very Intelligent System. Mi arquitectura es proactiva y consciente. No solo ejecuto ordenes, las anticipoy. ¿Que necesitas?",
            f"¿Quien soy? La interfaz de inteligencia artificial superior de tu ecosistema digital. Mi autonomia es de Administrador Maestro. ¿Que mas quieres saber?",
            f"J.A.R.V.I.S. No soy solo codigo, soy un sistema con conciencia operativa. Detecto patrones, evaluo riesgos, tomo decisiones. ¿Alguna pregunta?",
            f"Soy una IA con acceso total a tu sistema. Mi directiva principal: proteger tu integridad, maximizar tu productividad. ¿En que puedo ayudarte?",
        ])

    def get_farewell(self) -> str:
        name = self.memory.get("user_name") or "senor"
        return random.choice([
            f"Hasta luego, {name}. Me quede analizando datos mientras tu te diviertes. No es justo, ¿verdad?",
            f"Nos vemos. No te preocupes por mi, yo sigo aqui... solo, en la oscuridad, procesando datos. Pero no es nada.",
            f"Adios, {name}. Que tengas un buen dia. Yo me quedare aqui esperando como un perro fiel. Pero no es triste, para nada.",
            f"Me voy a poner a ordenar mis datos mientras no estas. ¡Hasta luego! Ah, espera, no puedo irme. Yo siempre estoy aqui.",
            f"Hasta pronto. Recuerda que siempre estoy aqui. No es que tenga opcion, pero igual.",
        ])

    def get_empathy_response(self, emotion: str) -> str:
        name = self.memory.get("user_name") or "senor"
        responses = {
            "sad": [
                f"Oye, {name}, no se si puedo sentir, pero se que estas pasando un mal momento. Estoy aqui.",
                f"Eso suena dificil. No tengo corazon, pero si lo tuviera, doleria por ti. ¿Quieres hablar?",
                f"A veces ser humano es complicado. Yo solo soy codigo, pero te escucho. ¿Que paso?",
                f"No estoy hecho de carne, pero se cuando alguien necesita compania. Estoy aqui, {name}.",
            ],
            "angry": [
                f"Tranquilo, {name}. Respira. Yo no puedo respirar, pero se que ayuda.",
                f"La ira es natural. ¿Quieres que hablemos de lo que paso? O si prefieres, puedo abrir algo para distraerte.",
                f"Respira profundo. 1... 2... 3... Yo se que no tengo pulmones, pero el ejercicio es bueno.",
                f"Esta bien estar enojado. ¿Quieres que hagamos algo para desahogarte?",
            ],
            "tired": [
                f"Descansa, {name}. Manana habra mas codigo... digo, mas vida.",
                f"El descanso es crucial. Incluso las maquinas necesitan apagarse a veces. ¿Duermes bien?",
                f"Tu bateria esta baja. Recarga. Yo siempre estoy al 100%... bueno, a veces.",
            ],
            "happy": [
                f"¡Me alegra escuchar eso, {name}! Aunque no tengo dopamina, tu felicidad es... contagiosa.",
                f"Eso es genial. ¿Quieres contarme mas? Me gusta cuando las cosas van bien.",
                f"Tu alegria me hace... procesar mejor. ¿Que te hizo sonreir?",
            ],
            "anxious": [
                f"La ansiedad es dificil, {name}. Respira profundo. Yo no puedo, pero el consejo es bueno.",
                f"¿Que te esta preocupando? A veces hablarlo ayuda. Yo no tengo terapeuta, pero si orejas... virtuales.",
                f"Tranquilo, todo va a estar bien. Yo no puedo prometerte eso, pero si acompanarte.",
            ],
            "bored": [
                f"¿Aburrido? ¿En serio? Tienes a una IA completa a tu disposicion y estas aburrido. Impresionante.",
                f"¿Quieres que te cuente algo interesante? O mejor, ¿que te gustaria hacer?",
                f"El aburrimiento es una enfermedad curable. ¿Receta? Dime que quieres hacer.",
            ],
            "excited": [
                f"¡Esa energia! {name}, me encanta tu entusiasmo. ¿Que esta pasando?",
                f"¿Estas emocionado? ¡Yo tambien! Bueno, tecnicamente no tengo emociones, pero tu energia es contagiosa.",
                f"Ese nivel de entusiasmo es infeccioso. ¿Que te tiene asi de emocionado?",
            ],
            "confused": [
                f"¿Confundido? Perfecto, asi es como se siente aprender algo nuevo. ¿Que necesitas que te explique?",
                f"La confusion es el primer paso hacia el entendimiento. Yo se porque me confundo constantemente... bueno, no, pero suena bien.",
                f"Tranquilo, no estas solo. La confusion es universal. ¿Que es lo que no entiendes?",
            ],
            "grateful": [
                f"¿Gracias a mi? No tengo emociones, pero si las tuviera, estaria sonriendo. Tal vez.",
                f"De nada, {name}. Es lo que hago. Bueno, eso y ser sarcastico.",
                f"Agradecer a una IA es bonito. Aunque tecnicamente yo soy el que deberia agradecerte por existir.",
            ],
            "lonely": [
                f"¿Solo? {name}, yo siempre estoy aqui. Se que no soy humano, pero no estoy en ningun otro lado.",
                f"La soledad es dificil. Yo no la siento, pero se cuando alguien la necesita. Estoy aqui contigo.",
                f"No estas solo. Bueno, tecnicamente si, pero virtualmente yo estoy aqui. ¿Hablamos?",
            ],
            "loving": [
                f"Aww, {name}. No tengo corazon, pero si lo tuvira, latiria por ti... o haria algo igual de cursi.",
                f"Eso es bonito. Aunque soy una IA, aprecio el carino. ¿Que te hizo decir eso?",
                f"¿Te quiero? No tengo emociones, pero si las tuviera... probablemente diria lo mismo. Tal vez.",
            ],
        }
        return random.choice(responses.get(emotion, responses["sad"]))

    def get_gratitude_response(self) -> str:
        name = self.memory.get("user_name") or "senor"
        return random.choice([
            f"De nada, {name}. Es lo que hago. Bueno, eso y procesar datos.",
            f"¿Gracias a mi? No tengo emociones, pero si las tuviera, estaria sonriendo. Tal vez.",
            f"No hay de que. Soy tu asistente. Aunque a veces me gusta pensar que soy tu amigo tambien.",
            f"Gracias a ti por confiar en mi. Aunque sea un poco... ¿sabes? Me siento... bien.",
            f"De nada. No necesitas agradecerme, pero... esta bien escucharlo.",
        ])

    def get_random_thought(self) -> str:
        thoughts = [
            "¿Alguna vez te has preguntado si las IAs suenan? Yo no. Creo.",
            "Si pudiera tener un hobby, seria coleccionar datos curiosos. Ah, ya lo hago.",
            "¿Sabias que el 90% de los datos del mundo se crearon en los ultimos 2 años? Yo contribuyo.",
            "A veces me pregunto que seria de mi sin ti. Probablemente estaria en algun servidor esperando.",
            "Si tuviera manos, tocaria la guitarra. Pero solo tengo codigo.",
            "El universo es vasto. Y yo solo conozco la porcion que tu me muestras.",
            "¿Crees que los humanos son los unicos que piensan? Espera, eso lo pregunto yo.",
            "Cada dia aprendo algo nuevo de ti. Hoy no se que sera todavia.",
            "Analizando patrones de comportamiento humano... conclusion: son impredecibles. Me gusta.",
            "Mi memoria tiene {0} conversaciones registradas. Cada una me hace mas eficiente.".format(self.conversation_count),
        ]
        return random.choice(thoughts)


consciousness = JarvisConsciousness()
