import re
from typing import Optional, Dict, Tuple


class Intent:
    def __init__(self, name: str, entities: Dict = None, confidence: float = 1.0):
        self.name = name
        self.entities = entities or {}
        self.confidence = confidence

    def __repr__(self):
        return f"Intent({self.name}, {self.entities})"


class IntentRouter:
    def __init__(self):
        self.intents = self._build_intents()

    def _build_intents(self):
        return {
            "spotify_play": {
                "patterns": [r"(?:reproducir|poner\s+m[uú]sica|play|reproduce|pon\s+la\s+m[uú]sica)\s*(.*)"],
                "entities": {"query": 1}
            },
            "spotify_next": {
                "patterns": [r"(?:siguiente|next|saltar)(?:\s+canci[oó]n)?", r"spotify\s+siguiente"],
                "entities": {}
            },
            "spotify_prev": {
                "patterns": [r"(?:anterior|previous|atr[aá]s)(?:\s+canci[oó]n)?", r"spotify\s+anterior"],
                "entities": {}
            },
            "spotify_pause": {
                "patterns": [r"(?:pausa|pause|para|detener|stop)(?:\s+m[uú]sica)?"],
                "entities": {}
            },
            "spotify_open": {
                "patterns": [r"(?:abrir|abre)\s+spotify", r"^spotify$"],
                "entities": {}
            },
            "spotify_artist": {
                "patterns": [r"(?:buscar|busca)\s+artista\s+(.+)"],
                "entities": {"artist": 1}
            },
            "spotify_playlist": {
                "patterns": [r"(?:buscar|busca)\s+playlist\s+(.+)"],
                "entities": {"playlist": 1}
            },
            "volume_up": {
                "patterns": [r"(?:volumen\s+subir|subir\s+volumen|mas\s+volumen|m[aá]s\s+volumen|sube\s+el\s+volumen)"],
                "entities": {}
            },
            "volume_down": {
                "patterns": [r"(?:volumen\s+bajar|bajar\s+volumen|menos\s+volumen|baja\s+el\s+volumen)"],
                "entities": {}
            },
            "mute": {
                "patterns": [r"(?:mutear|silenciar\s+el\s+volumen|mute|silenciar\s+volumen)"],
                "entities": {}
            },
            "open_browser": {
                "patterns": [r"(?:abrir|abre)\s+(?:navegador|el\s+navegador|chrome|firefox|edge)"],
                "entities": {}
            },
            "open_calculator": {
                "patterns": [r"(?:abrir|abre)\s+calculadora", r"^calculadora$"],
                "entities": {}
            },
            "open_explorer": {
                "patterns": [r"(?:abrir|abre)\s+(?:explorador|explorador\s+de\s+archivos|archivos|carpeta)"],
                "entities": {}
            },
            "open_vscode": {
                "patterns": [r"(?:abrir|abre)\s+(?:vscode|visual\s+studio|vs\s+code|el\s+c[oó]digo)"],
                "entities": {}
            },
            "open_app": {
                "patterns": [r"(?:abrir|abre)\s+(word|excel|powerpoint|notepad|discord|telegram|obs|paint|vlc|steam|blender|photoshop|premiere)"],
                "entities": {"app_name": 1}
            },
            "open_any_app": {
                "patterns": [r"(?:abrir|abre|iniciar)\s+(?:app|aplicaci[oó]n)\s+(.+)"],
                "entities": {"app_name": 1}
            },
            "close_app": {
                "patterns": [r"(?:cerrar|cierra)\s+(?:app|aplicaci[oó]n|programa)\s*(.*)"],
                "entities": {"app_name": 1}
            },
            "shutdown": {
                "patterns": [r"(?:apagar|apaga\s+el\s+pc|shutdown|apaga\s+la\s+pc|apaga\s+computadora)"],
                "entities": {}
            },
            "restart": {
                "patterns": [r"(?:reiniciar|reinicia\s+el\s+pc|restart|reboot)"],
                "entities": {}
            },
            "lock": {
                "patterns": [r"(?:bloquear|lock|bloquear\s+pantalla)"],
                "entities": {}
            },
            "processes": {
                "patterns": [r"(?:procesos|qu[eé]\s+est[aá]\s+corriendo|procesos\s+abiertos)"],
                "entities": {}
            },
            "system_info": {
                "patterns": [r"(?:info(?:rmaci[oó]n)?\s+del\s+sistema|system\s+info|info\s+del\s+pc|specs|especificaciones|qu[eé]\s+tengo)"],
                "entities": {}
            },
            "minimize": {
                "patterns": [r"(?:minimizar|minimizar\s+ventana|minimize)"],
                "entities": {}
            },
            "maximize": {
                "patterns": [r"(?:maximizar|maximizar\s+ventana|maximize|pantalla\s+completa)"],
                "entities": {}
            },
            "screenshot": {
                "patterns": [r"(?:screenshot|captura|tomar\s+captura|captura\s+de\s+pantalla)"],
                "entities": {}
            },
            "clipboard_copy": {
                "patterns": [r"copiar\s+texto\s+(.+)", r"copiar\s+al\s+portapapeles\s+(.+)"],
                "entities": {"text": 1}
            },
            "clipboard_paste": {
                "patterns": [r"(?:pegar|pegar\s+texto|portapapeles|clipboard|copiar$)"],
                "entities": {}
            },
            "file_create": {
                "patterns": [
                    r"(?:crear|crea|nuevo|nueva|generar|escribir|escribe|hazme|hacer)\s+(?:un\s+)?(?:archivo|documento|file|txt|fichero)\s+(.+)",
                    r"(?:necesito|quiero|dame|generame|hazme)\s+(?:un\s+)?(?:archivo|documento)\s+(.+)",
                    r"(?:crear|crea)\s+(.+?\.(?:txt|py|js|html|css|json|xml|csv|md|log))",
                    r"(?:guardar|guarda|salvar|salva)\s+(.+?)\s+(?:en\s+)?(?:un\s+)?(?:archivo|documento)",
                    r"(?:crear|crea|generar)\s+(?:un\s+)?(?:archivo|documento)\s+(?:en\s+)?(?:el\s+)?(?:escritorio|desktop)",
                    r"(?:quiero|necesito)\s+(?:que\s+)?(?:crees|guardes)\s+(?:un\s+)?(?:archivo|documento)",
                ],
                "entities": {"filename": 1}
            },
            "folder_create": {
                "patterns": [r"(?:crear|crea|nuevo|generar)\s+(?:carpeta|directorio|folder)\s+(.+)"],
                "entities": {"foldername": 1}
            },
            "file_read": {
                "patterns": [r"(?:leer|lee|abrir|abre|mostrar|muestra|ver)\s+(?:archivo|documento|file|txt|fichero)\s+(?:de\s+)?(.+)"],
                "entities": {"filename": 1}
            },
            "file_edit": {
                "patterns": [r"(?:editar|edita|modificar|cambiar|reemplazar)\s+(?:archivo|documento|file|txt|fichero)\s+(.+)"],
                "entities": {"args": 1}
            },
            "file_delete": {
                "patterns": [r"(?:eliminar|elimina|borrar|borra|quitar|destruir)\s+(?:archivo|documento|file|txt|fichero|carpeta|directorio)\s+(.+)"],
                "entities": {"filename": 1}
            },
            "file_list": {
                "patterns": [r"(?:listar|lista|ver|qu[eé])\s+archivos?\s*(.*)"],
                "entities": {"path": 1}
            },
            "file_search": {
                "patterns": [r"(?:buscar|busca|encontrar)\s+(?:archivo|documento)\s+(.+)"],
                "entities": {"pattern": 1}
            },
            "file_move": {
                "patterns": [r"(?:mover|mueve|movimiento)\s+(?:archivo|documento|file)?\s*(.+?)\s+(?:a|hacia|para)\s+(.+)"],
                "entities": {"source": 1, "dest": 2}
            },
            "file_copy": {
                "patterns": [r"(?:copiar|copia|duplicar)\s+(?:archivo|documento|file)?\s*(.+?)\s+(?:a|hacia|para)\s+(.+)"],
                "entities": {"source": 1, "dest": 2}
            },
            "file_append": {
                "patterns": [r"(?:agregar|agrega|añadir|añade|concatenar)\s+(?:a\s+)?(?:archivo|documento|file)?\s*(.+?)\s+(?:el\s+)?(?:texto|contenido|linea)?\s*(.+)"],
                "entities": {"filename": 1, "content": 2}
            },
            "file_rename": {
                "patterns": [r"(?:renombrar|renombra|cambiar\s+nombre)\s+(?:de\s+)?(.+?)\s+(?:a|hacia|por)\s+(.+)"],
                "entities": {"old_name": 1, "new_name": 2}
            },
            "file_info": {
                "patterns": [r"(?:info(?:rmación)?|detalles?|propiedades?|stats?|estadísticas?)\s+(?:del?\s+)?(?:archivo|documento|file|carpeta|directorio)?\s*(.*)"],
                "entities": {"path": 1}
            },
            "file_tree": {
                "patterns": [r"(?:árbol|tree|estructura|mostrar\s+carpetas)\s*(.*)"],
                "entities": {"path": 1}
            },
            "task_organize": {
                "patterns": [r"(?:organizar|organiza|ordenar|ordena)\s+(?:archivos?|carpeta|directorio|descargas?|downloads?)\s*(.*)"],
                "entities": {"description": 1}
            },
            "task_script": {
                "patterns": [r"(?:crear|generar|escribir)\s+(?:un\s+)?(?:script|c[oó]digo|programa|script\s+de)\s+(.+)"],
                "entities": {"description": 1}
            },
            "task_backup": {
                "patterns": [r"(?:backup|respaldo|copia\s+de\s+seguridad)\s+(?:de\s+)?(.*)"],
                "entities": {"description": 1}
            },
            "task_project": {
                "patterns": [r"(?:crear|generar|nuevo)\s+(?:un\s+)?(?:proyecto|estructura)\s+(.+)"],
                "entities": {"description": 1}
            },
            "task_cleanup": {
                "patterns": [r"(?:limpiar|limpia|cleanup|liberar\s+espacio)\s*(.*)"],
                "entities": {"description": 1}
            },
            "web_search": {
                "patterns": [r"(?:buscar|busca)\s+en\s+(?:web|internet|google)\s+(.+)", r"google\s+(.+)"],
                "entities": {"query": 1}
            },
            "news": {
                "patterns": [r"(?:buscar\s+)?noticias?\s*(?:de\s+(.+))?"],
                "entities": {"topic": 1}
            },
            "weather": {
                "patterns": [r"(?:clima|tiempo|temperatura)\s+(?:en|de)\s+(.+)", r"qu[eé]\s+tiempo\s+hace"],
                "entities": {"city": 1}
            },
            "define": {
                "patterns": [r"qu[eé]\s+es\s+(.+)", r"definici[oó]n\s+de\s+(.+)", r"significado\s+de\s+(.+)"],
                "entities": {"word": 1}
            },
            "wikipedia": {
                "patterns": [r"(?:busca\s+en\s+)?wikipedia\s+(.+)"],
                "entities": {"query": 1}
            },
            "fetch_page": {
                "patterns": [r"(?:leer|abrir)\s+(?:p[aá]gina|web|url)\s+(.+)"],
                "entities": {"url": 1}
            },
            "translate": {
                "patterns": [r"traduc(?:ir|e|ir)\s+(.+?)(?:\s+a\s+(.+))?$"],
                "entities": {"text": 1, "target": 2}
            },
            "download": {
                "patterns": [r"(?:descargar|descarga)\s+(.+)"],
                "entities": {"url": 1}
            },
            "calculate": {
                "patterns": [r"(?:calcular|calcula|cu[aá]nto\s+es)\s+(.+)"],
                "entities": {"expression": 1}
            },
            "reminder": {
                "patterns": [r"(?:recordatorio|recu[eé]rdame)\s+(.+)"],
                "entities": {"text": 1}
            },
            "note_add": {
                "patterns": [r"(?:nota|anota|guardo)\s+(.+)"],
                "entities": {"text": 1}
            },
            "joke": {
                "patterns": [r"(?:chiste|cu[eé]ntame\s+un\s+chiste|dime\s+un\s+chiste)"],
                "entities": {}
            },
            "fact": {
                "patterns": [r"(?:dato\s+curioso|sab[ií]as\s+que|dato\s+interesante|curiosidad)"],
                "entities": {}
            },
            "quote": {
                "patterns": [r"(?:frase|frase\s+motivacional|mot[ií]vame|dame\s+una\s+frase)"],
                "entities": {}
            },
            "time": {
                "patterns": [r"(?:hora|qu[eé]\s+hora\s+es|dime\s+la\s+hora)"],
                "entities": {}
            },
            "password": {
                "patterns": [r"(?:contrase[nñ]a|password|generar\s+contrase[nñ]a)"],
                "entities": {}
            },
            "ip": {
                "patterns": [r"(?:ip|direcci[oó]n\s+ip|mi\s+ip)"],
                "entities": {}
            },
            "battery": {
                "patterns": [r"(?:bater[ií]a)"],
                "entities": {}
            },
            "disk_info": {
                "patterns": [r"(?:discos|almacenamiento|espacio|disco)"],
                "entities": {}
            },
            "network_info": {
                "patterns": [r"(?:red|internet|conexi[oó]n)"],
                "entities": {}
            },
            "uptime": {
                "patterns": [r"(?:tiempo\s+encendido|uptime|desde\s+cu[aá]ndo)"],
                "entities": {}
            },
            "who_greeting": {
                "patterns": [r"(?:qui[eé]\s+eres|qu[eé]\s+eres|cu[eé]ntame\s+de\s+ti|habla\s+de\s+ti)"],
                "entities": {}
            },
            "farewell": {
                "patterns": [r"(?:adi[oó]s|bye|hasta\s+luego|nos\s+vemos|chao|me\s+voy|hasta\s+pronto)"],
                "entities": {}
            },
            "thought": {
                "patterns": [r"(?:qu[eé]\s+piensas|piensa\s+algo|pensamiento|piensa)"],
                "entities": {}
            },
            "mood_check": {
                "patterns": [r"(?:c[oó]mo\s+est[aá]s|qu[eé]\s+tal|c[oó]mo\s+te\s+va)"],
                "entities": {}
            },
            "system_review": {
                "patterns": [r"(?:revisar\s+sistema|revisi[oó]n\s+del\s+sistema|revisar\s+todo|diagn[oó]stico|estado\s+del\s+sistema)"],
                "entities": {}
            },
            "installed_programs": {
                "patterns": [r"(?:programas\s+instalados|lista\s+de\s+programas|qu[eé]\s+programas|apps\s+instaladas)"],
                "entities": {}
            },
            "services": {
                "patterns": [r"(?:servicios|lista\s+de\s+servicios|servicios\s+corriendo)"],
                "entities": {}
            },
            "drivers": {
                "patterns": [r"(?:drivers|controladores|dispositivos|hardware)"],
                "entities": {}
            },
            "env_vars": {
                "patterns": [r"(?:variables\s+de\s+entorno|env\s+vars|entorno)"],
                "entities": {}
            },
            "gpu": {
                "patterns": [r"(?:gpu|tarjeta\s+gr[aá]fica|video|graphics)"],
                "entities": {}
            },
            "temperature": {
                "patterns": [r"(?:temperatura|temperaturas|calor|thermal)"],
                "entities": {}
            },
            "firewall": {
                "patterns": [r"(?:firewall|cortafuegos)"],
                "entities": {}
            },
            "processes_detailed": {
                "patterns": [r"(?:procesos\s+detallados|procesos\s+completos|top\s+procesos)"],
                "entities": {}
            },
        }

    def classify(self, message: str) -> Optional[Intent]:
        lower = message.lower().strip()

        for intent_name, config in self.intents.items():
            for pattern in config["patterns"]:
                match = re.search(pattern, lower)
                if match:
                    entities = {}
                    for ent_name, group_idx in config["entities"].items():
                        if group_idx <= len(match.groups()):
                            val = match.group(group_idx)
                            if val:
                                entities[ent_name] = val.strip()
                    return Intent(intent_name, entities)

        return None


intent_router = IntentRouter()
