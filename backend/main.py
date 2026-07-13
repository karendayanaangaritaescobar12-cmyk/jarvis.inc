import os
import json
import re
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

from ai_providers import get_provider
from system_control import system_controller
from utilities import utilities
from consciousness import consciousness
from web_access import web

load_dotenv()

app = FastAPI(title="JARVIS AI Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_provider = get_provider()
chat_history = []


class ChatMessage(BaseModel):
    message: str
    voice: bool = False


class ExecuteRequest(BaseModel):
    command: str
    type: str = "powershell"


class ChatResponse(BaseModel):
    response: str
    action: Optional[str] = None


def execute_ai_actions(text: str) -> str:
    exec_pattern = r'\[EXEC:\s*(.+?)\]'
    matches = re.findall(exec_pattern, text)
    results = []
    for cmd in matches:
        cmd = cmd.strip()
        output = system_controller.run_powershell(cmd) if not any(
            x in cmd.lower() for x in ["pip ", "npm ", "apt ", "winget "]
        ) else system_controller.run_cmd(cmd)
        results.append(f"[Resultado de '{cmd}']:\n{output}")
    text = re.sub(exec_pattern, '', text).strip()
    if results:
        text += "\n\n" + "\n".join(results)
    return text


def process_command(msg: str) -> Optional[str]:
    lower = msg.lower().strip()

    # Helper: check if any of the triggers appear in the message
    def has_any(text, triggers):
        return any(t in text for t in triggers)

    # === SPOTIFY / MEDIOS ===
    if has_any(lower, ["reproducir", "poner música", "poner musica", "play", "reproduce", "pon la música", "pon música"]):
        if "spotify" in lower:
            return system_controller.open_spotify()
        if has_any(lower, ["siguiente", "next", "saltar"]):
            return system_controller.spotify_next()
        if has_any(lower, ["anterior", "previous", "atrás", "atras"]):
            return system_controller.spotify_prev()
        if has_any(lower, ["pausa", "pause", "para", "detener", "stop"]):
            return system_controller.spotify_play_pause()
        return system_controller.open_spotify()
    if has_any(lower, ["spotify siguiente", "siguiente canción", "siguiente cancion", "next track"]):
        return system_controller.spotify_next()
    if has_any(lower, ["spotify anterior", "canción anterior", "cancion anterior", "previous track"]):
        return system_controller.spotify_prev()
    if has_any(lower, ["pausa música", "pausa musica", "parar música", "parar musica", "pause music"]):
        return system_controller.spotify_play_pause()
    if has_any(lower, ["subir volumen música", "subir volumen musica", "volume up"]):
        return system_controller.spotify_volume_up()
    if has_any(lower, ["bajar volumen música", "bajar volumen musica", "volume down"]):
        return system_controller.spotify_volume_down()
    if has_any(lower, ["silenciar música", "silenciar musica", "mute music"]):
        return system_controller.spotify_mute()
    if has_any(lower, ["abrir spotify", "abre spotify", "spotify"]):
        return system_controller.open_spotify()
    if has_any(lower, ["buscar artista", "busca artista", "search artist"]):
        artist = msg.split("artista")[-1].strip() if "artista" in lower else msg.replace("buscar artista", "").replace("busca artista", "").strip()
        return system_controller.spotify_open_artist(artist)
    if has_any(lower, ["buscar playlist", "busca playlist", "search playlist"]):
        playlist = msg.split("playlist")[-1].strip() if "playlist" in lower else msg.replace("buscar playlist", "").replace("busca playlist", "").strip()
        return system_controller.spotify_open_playlist(playlist)

    # === ABRIR / CERRAR APPS ===
    if has_any(lower, ["abrir navegador", "abre el navegador", "abre navegador", "navegador", "internet", "chrome", "firefox", "edge"]):
        if "firefox" in lower:
            return system_controller.open_app("firefox")
        if "edge" in lower:
            return system_controller.open_app("edge")
        return system_controller.open_browser()
    if has_any(lower, ["abrir calculadora", "abre calculadora", "calculadora"]):
        return system_controller.open_calculator()
    if has_any(lower, ["abrir explorador", "abre explorador", "explorador de archivos", "explorador", "archivos", "carpeta"]):
        return system_controller.open_explorer()
    if has_any(lower, ["abrir vscode", "abre vscode", "abre visual", "visual studio", "vs code", "vscode", "abre el codigo", "abre código", "abrir código"]):
        return system_controller.open_vscode()
    if has_any(lower, ["abrir word", "abre word", "microsoft word", "word"]):
        return system_controller.open_app("word")
    if has_any(lower, ["abrir excel", "abre excel", "excel"]):
        return system_controller.open_app("excel")
    if has_any(lower, ["abrir powerpoint", "abre powerpoint", "abrir presentación", "powerpoint"]):
        return system_controller.open_app("powerpoint")
    if has_any(lower, ["abrir notepad", "abre notepad", "bloc de notas", "notepad"]):
        return system_controller.open_app("notepad")
    if has_any(lower, ["abrir discord", "abre discord", "discord"]):
        return system_controller.open_app("discord")
    if has_any(lower, ["abrir telegram", "abre telegram", "telegram"]):
        return system_controller.open_app("telegram")
    if has_any(lower, ["abrir obs", "abre obs", "abrir obs studio", "obs studio", "obs"]):
        return system_controller.open_app("obs")
    if has_any(lower, ["abrir terminal", "abre terminal", "abrir powershell", "abre powershell", "abrir cmd", "abre cmd", "abrir consola", "abre consola", "terminal", "powershell", "cmd"]):
        return system_controller.open_app("terminal")
    if has_any(lower, ["abrir paint", "abre paint", "paint"]):
        return system_controller.open_app("paint")
    if has_any(lower, ["abrir vlc", "abre vlc", "abrir reproductor", "vlc"]):
        return system_controller.open_app("vlc")
    if has_any(lower, ["abrir steam", "abre steam", "steam"]):
        return system_controller.open_app("steam")
    if has_any(lower, ["abrir blender", "abre blender", "blender"]):
        return system_controller.open_app("blender")
    if has_any(lower, ["abrir photoshop", "abre photoshop", "photoshop"]):
        return system_controller.open_app("photoshop")
    if has_any(lower, ["abrir premiere", "abre premiere", "premiere"]):
        return system_controller.open_app("premiere")
    if has_any(lower, ["abrir app", "abre app", "abrir aplicación", "abre aplicación", "iniciar app", "iniciar aplicación"]):
        app_name = msg.replace("abrir app", "").replace("abre app", "").replace("abrir aplicación", "").replace("abre aplicación", "").replace("iniciar app", "").replace("iniciar aplicación", "").strip()
        return system_controller.open_app(app_name)
    if has_any(lower, ["cerrar app", "cierra app", "cerrar aplicación", "cierra aplicación", "cerrar programa", "cierra programa"]):
        app_name = msg.replace("cerrar app", "").replace("cierra app", "").replace("cerrar aplicación", "").replace("cierra aplicación", "").replace("cerrar programa", "").replace("cierra programa", "").strip()
        return system_controller.close_app(app_name)

    # === SISTEMA ===
    if has_any(lower, ["apagar", "apaga el pc", "shutdown", "apaga la pc", "apaga computadora", "apagar computadora"]):
        return system_controller.shutdown()
    if has_any(lower, ["reiniciar", "reinicia el pc", "restart", "reinicia la pc", "reboot"]):
        return system_controller.restart()
    if has_any(lower, ["bloquear", "bloquear pc", "lock", "bloquear pantalla"]):
        return system_controller.lock_screen()
    if has_any(lower, ["volumen subir", "subir volumen", "mas volumen", "más volumen", "sube el volumen", "más volumen"]):
        return system_controller.change_volume("up")
    if has_any(lower, ["volumen bajar", "bajar volumen", "menos volumen", "baja el volumen"]):
        return system_controller.change_volume("down")
    if has_any(lower, ["mutear", "silenciar el volumen", "mute", "silenciar volumen"]):
        return system_controller.mute_volume()
    if has_any(lower, ["procesos", "qué está corriendo", "que esta corriendo", "qué corre", "que corre", "procesos abiertos"]):
        return system_controller.get_running_processes()
    if has_any(lower, ["información del sistema", "informacion del sistema", "system info", "info del sistema", "info del pc", "información del pc", "qué tengo", "que tengo", "specs", "especificaciones"]):
        info = system_controller.get_system_info()
        bat = info.get('battery')
        bat_str = f"\nBatería: {bat['percent']}% ({'Cargando' if bat['power_plugged'] else 'Sin carga'})" if bat else ""
        return f"Sistema: {info['system']} {info['version']}\nCPU: {info['cpu_percent']}%\nMemoria: {info['memory']['percent']}%{bat_str}"

    # === VENTANAS ===
    if has_any(lower, ["minimizar", "minimizar ventana", "minimize", "minimizar todo"]):
        return system_controller.minimize_window()
    if has_any(lower, ["maximizar", "maximizar ventana", "maximize", "pantalla completa", "maximizar ventana"]):
        return system_controller.maximize_window()
    if has_any(lower, ["screenshot", "captura", "tomar captura", "captura de pantalla", "capturar pantalla"]):
        return system_controller.screenshot()

    # === PORTAPAPELES ===
    if has_any(lower, ["copiar texto", "copiar al portapapeles"]):
        text = msg.replace("copiar texto", "").replace("copiar al portapapeles", "").strip()
        if text:
            return system_controller.set_clipboard(text)
        return system_controller.get_clipboard()
    if has_any(lower, ["pegar", "pegar texto", "portapapeles", "clipboard", "copiar"]):
        return system_controller.get_clipboard()

    # === ARCHIVOS (acepta "archivo", "documento", "file", "txt") ===
    file_aliases = ["archivo", "documento", "file", "txt", "fichero"]
    create_words = ["crear", "crea", "nuevo", "nueva", "generar", "genera", "escribir", "escribe"]
    folder_words = ["carpeta", "directorio", "folder"]

    # Crear archivo/documento
    if has_any(lower, create_words) and has_any(lower, file_aliases):
        parts = lower
        for w in create_words + file_aliases + ["el ", "la ", "un ", "una ", "lo "]:
            parts = parts.replace(w, "")
        parts = parts.strip()
        if "|" in parts:
            name, content = parts.split("|", 1)
            return system_controller.create_file(name.strip(), content.strip())
        return system_controller.create_file(parts, "") if parts else "¿Nombre del archivo?"
    # Crear carpeta/directorio
    if has_any(lower, create_words) and has_any(lower, folder_words):
        parts = lower
        for w in create_words + folder_words + ["el ", "la ", "un ", "una ", "lo "]:
            parts = parts.replace(w, "")
        parts = parts.strip()
        return system_controller.create_directory(parts) if parts else "¿Nombre de la carpeta?"

    # Leer archivo/documento
    read_words = ["leer", "lee", "abrir", "abre", "mostrar", "muestra", "ver", "contenido de"]
    if has_any(lower, read_words) and has_any(lower, file_aliases):
        path = lower
        for w in read_words + file_aliases + ["el ", "la ", "un ", "una ", "lo ", "de "] + ["contenido"]:
            path = path.replace(w, "")
        path = path.strip()
        return system_controller.read_file(path) if path else "¿Qué archivo quieres leer?"

    # Editar archivo/documento
    edit_words = ["editar", "edita", "modificar", "modifica", "cambiar", "cambia", "reemplazar", "reemplaza"]
    if has_any(lower, edit_words) and has_any(lower, file_aliases):
        parts = lower
        for w in edit_words + file_aliases + ["el ", "la ", "un ", "una ", "lo "]:
            parts = parts.replace(w, "")
        parts = parts.strip()
        if "|" in parts:
            path, rest = parts.split("|", 1)
            if "|" in rest:
                old_text, new_text = rest.split("|", 1)
                return system_controller.edit_file(path.strip(), old_text.strip(), new_text.strip())
        return "Formato: editar archivo [nombre] | [texto viejo] | [texto nuevo]"

    # Agregar texto a archivo
    append_words = ["agregar texto", "agrega texto", "añadir texto", "append", "agregar", "agrega", "añadir"]
    if has_any(lower, append_words) and has_any(lower, file_aliases):
        parts = lower
        for w in append_words + file_aliases + ["el ", "la ", "un ", "una ", "lo ", "texto", "a ", "al "]:
            parts = parts.replace(w, "")
        parts = parts.strip()
        if "|" in parts:
            path, content = parts.split("|", 1)
            return system_controller.append_file(path.strip(), content.strip())
        return "Formato: agregar texto [archivo] | [contenido]"

    # Insertar texto en archivo
    if has_any(lower, ["insertar texto", "inserta texto"]):
        parts = lower.replace("insertar texto", "").replace("inserta texto", "").strip()
        if "|" in parts:
            path, rest = parts.split("|", 1)
            if "|" in rest:
                line, content = rest.split("|", 1)
                return system_controller.insert_file(path.strip(), int(line.strip()), content.strip())
        return "Formato: insertar texto [archivo] | [línea] | [contenido]"

    # Renombrar
    if has_any(lower, ["renombrar", "rename"]):
        parts = lower.replace("renombrar", "").replace("archivo", "").replace("carpeta", "").replace("documento", "").replace("a ", "").strip()
        if "|" in parts:
            old, new = parts.split("|", 1)
            return system_controller.rename_file(old.strip(), new.strip())
        if " a " in parts:
            old, new = parts.split(" a ", 1)
            return system_controller.rename_file(old.strip(), new.strip())
        return "Formato: renombrar [viejo] | [nuevo]"

    # Copiar archivo
    if has_any(lower, ["copiar archivo", "copia archivo", "copiar documento"]):
        parts = lower.replace("copiar archivo", "").replace("copia archivo", "").replace("copiar documento", "").strip()
        if "|" in parts:
            src, dst = parts.split("|", 1)
            return system_controller.copy_file(src.strip(), dst.strip())
        if " a " in parts:
            src, dst = parts.split(" a ", 1)
            return system_controller.copy_file(src.strip(), dst.strip())
        return "Formato: copiar archivo [origen] | [destino]"

    # Mover archivo
    if has_any(lower, ["mover archivo", "mueve archivo", "mover documento"]):
        parts = lower.replace("mover archivo", "").replace("mueve archivo", "").replace("mover documento", "").strip()
        if "|" in parts:
            src, dst = parts.split("|", 1)
            return system_controller.move_file(src.strip(), dst.strip())
        if " a " in parts:
            src, dst = parts.split(" a ", 1)
            return system_controller.move_file(src.strip(), dst.strip())
        return "Formato: mover archivo [origen] | [destino]"

    # Eliminar archivo
    delete_words = ["eliminar", "elimina", "borrar", "borra", "quitar", "quita", "destruir", "destruye"]
    if has_any(lower, delete_words) and has_any(lower, file_aliases + folder_words):
        path = lower
        for w in delete_words + file_aliases + folder_words + ["el ", "la ", "un ", "una ", "lo "]:
            path = path.replace(w, "")
        path = path.strip()
        return system_controller.delete_file(path) if path else "¿Qué quieres eliminar?"

    # Info archivo
    if has_any(lower, ["info archivo", "información archivo", "propiedades archivo", "info documento", "propiedades"]):
        path = lower.replace("info archivo", "").replace("información archivo", "").replace("propiedades archivo", "").replace("info documento", "").replace("propiedades", "").strip()
        return system_controller.file_info(path) if path else "¿De qué archivo?"

    # Listar archivos
    if has_any(lower, ["listar archivos", "lista archivos", "ver archivos", "qué archivos", "que archivos", "qué tengo", "que tengo en", "archivos que hay", "listar"]):
        path = lower.replace("listar archivos", "").replace("lista archivos", "").replace("ver archivos", "").replace("qué archivos", "").replace("que archivos", "").replace("qué tengo", "").replace("que tengo en", "").replace("archivos que hay", "").replace("listar", "").strip()
        return system_controller.list_files(path or ".")

    # Buscar archivo
    if has_any(lower, ["buscar archivo", "busca archivo", "encontrar archivo", "buscar documento", "buscar file"]):
        pattern = lower.replace("buscar archivo", "").replace("busca archivo", "").replace("encontrar archivo", "").replace("buscar documento", "").replace("buscar file", "").strip()
        return system_controller.search_files(pattern) if pattern else "¿Qué patrón buscar?"

    # Buscar contenido
    if has_any(lower, ["buscar en archivos", "buscar texto en", "buscar contenido", "buscar en documentos"]):
        text = lower.replace("buscar en archivos", "").replace("buscar texto en", "").replace("buscar contenido", "").replace("buscar en documentos", "").strip()
        return system_controller.search_file_content(text) if text else "¿Qué texto buscar?"

    # Árbol
    if has_any(lower, ["árbol", "arbol", "tree", "estructura de carpetas", "estructura"]):
        path = lower.replace("árbol", "").replace("arbol", "").replace("tree", "").replace("estructura de carpetas", "").replace("estructura", "").strip()
        return system_controller.tree_view(path or ".", 2)

    # === REVISIÓN DEL SISTEMA ===
    if has_any(lower, ["revisar sistema", "revisión del sistema", "revision del sistema", "revisar todo", "revisión completa", "estado del sistema", "revisa el sistema", "chequear sistema", "chequea sistema", "diagnóstico", "diagnostico"]):
        return system_controller.system_review()
    if has_any(lower, ["programas instalados", "lista de programas", "qué programas", "que programas", "apps instaladas", "qué apps", "qué hay instalado", "que hay instalado"]):
        return system_controller.list_installed_programs()
    if has_any(lower, ["servicios", "lista de servicios", "servicios corriendo", "qué servicios", "que servicios"]):
        return system_controller.list_services()
    if has_any(lower, ["programas de inicio", "startup", "inician con windows", "autoarranque", "qué inicia", "que inicia"]):
        return system_controller.list_startup_programs()
    if has_any(lower, ["drivers", "controladores", "dispositivos", "hardware", "qué hardware", "que hardware"]):
        return system_controller.list_drivers()
    if has_any(lower, ["variables de entorno", "env vars", "entorno", "environment"]):
        return system_controller.list_environment_paths()
    if has_any(lower, ["tareas programadas", "scheduled tasks", "tareas de windows", "tareas automáticas"]):
        return system_controller.list_scheduled_tasks()
    if has_any(lower, ["salud discos", "estado discos", "disk health", "smart", "salud del disco"]):
        return system_controller.check_disk_health()
    if has_any(lower, ["actualizaciones", "updates", "windows update", "patches", "qué actualizaciones"]):
        return system_controller.check_windows_updates()
    if has_any(lower, ["usuarios", "cuentas", "user accounts", "quién usa", "quien usa", "qué usuarios", "que usuarios"]):
        return system_controller.get_user_accounts()
    if has_any(lower, ["puertos abiertos", "open ports", "listening ports", "puertos"]):
        return system_controller.get_open_ports()
    if has_any(lower, ["todas las unidades", "discos duros", "all drives", "unidades de disco", "unidades", "discos"]):
        return system_controller.get_all_drives()

    # === ANÁLISIS PROFUNDO DEL SISTEMA ===
    if has_any(lower, ["procesos detallados", "procesos completos", "detalles de procesos", "top procesos", "detalles procesos"]):
        return system_controller.detailed_processes()
    if has_any(lower, ["gpu", "tarjeta gráfica", "tarjeta grafica", "video", "graphics", "gráfica", "grafica"]):
        return system_controller.gpu_info()
    if has_any(lower, ["temperatura", "temperaturas", "temperature", "calor", "thermal", "cuánto calor", "cuanto calor"]):
        return system_controller.temperature_info()
    if has_any(lower, ["firewall", "cortafuegos"]):
        if "reglas" in lower or "rules" in lower:
            return system_controller.firewall_rules()
        return system_controller.firewall_status()
    if has_any(lower, ["conexiones activas", "conexiones", "active connections", "qué está conectado", "que esta conectado", "conexiones de red"]):
        return system_controller.active_connections()
    if has_any(lower, ["logs del sistema", "system logs", "eventos del sistema", "errores del sistema", "logs", "eventos"]):
        return system_controller.system_logs()
    if has_any(lower, ["logs de aplicaciones", "application logs", "errores de apps", "logs de apps"]):
        return system_controller.application_logs()
    if has_any(lower, ["codecs", "códecs"]):
        return system_controller.installed_codecs()
    if has_any(lower, ["adaptadores de red", "network adapters", "interfaces de red", "adaptadores", "tarjetas de red"]):
        return system_controller.network_adapters()
    if has_any(lower, ["wifi", "perfiles wifi", "redes wifi", "wlan", "red wifi"]):
        return system_controller.wifi_profiles()
    if has_any(lower, ["plan de energía", "power plan", "energía", "batería plan", "plan electricidad"]):
        return system_controller.power_plan()
    if has_any(lower, ["startup detallado", "inicio detallado", "startup programs detailed", "inicio avanzado"]):
        return system_controller.startup_programs_detailed()
    if has_any(lower, ["info completa", "información completa del sistema", "full system info", "todo del sistema", "info del pc completa", "especificaciones completas"]):
        return system_controller.system_info_full()

    # === WEB ===
    if has_any(lower, ["buscar en web", "buscar en internet", "busca en web", "busca en internet", "google", "buscar en google", "buscar algo", "busca algo"]):
        query = msg.replace("buscar en web", "").replace("buscar en internet", "").replace("busca en web", "").replace("busca en internet", "").replace("google", "").replace("buscar en google", "").replace("buscar algo", "").replace("busca algo", "").strip()
        if query:
            return web.search_google(query)
        return "¿Qué quieres buscar?"
    if has_any(lower, ["buscar noticias", "noticias de", "últimas noticias", "ultimas noticias", "qué noticias", "que noticias"]):
        query = msg.replace("buscar noticias", "").replace("noticias de", "").replace("últimas noticias", "").replace("ultimas noticias", "").replace("qué noticias", "").replace("que noticias", "").strip()
        return web.get_news(query or "general")
    if has_any(lower, ["clima en", "tiempo en", "temperatura en", "clima de", "tiempo de", "qué tiempo", "que tiempo"]):
        city = msg.split("en")[-1].strip() if "en" in lower else msg.split("de")[-1].strip() if "de" in lower else msg.split("qué tiempo")[-1].strip() if "qué tiempo" in lower else msg.split("que tiempo")[-1].strip() if "que tiempo" in lower else "Madrid"
        return web.get_weather(city or "Madrid")
    if has_any(lower, ["qué es", "que es", "definición de", "definicion de", "significado de", "qué significa", "que significa"]):
        word = msg.replace("qué es", "").replace("que es", "").replace("definición de", "").replace("definicion de", "").replace("significado de", "").replace("qué significa", "").replace("que significa", "").strip()
        return web.get_wikipedia(word) if word else "¿Qué quieres definir?"
    if has_any(lower, ["wikipedia", "busca en wikipedia", "buscar en wikipedia"]):
        query = msg.replace("wikipedia", "").replace("busca en wikipedia", "").replace("buscar en wikipedia", "").strip()
        return web.get_wikipedia(query) if query else "¿Qué buscas en Wikipedia?"
    if has_any(lower, ["leer página", "leer web", "abrir página", "abrir web", "fetch", "scrapear", "scrape", "leer url"]):
        url = msg.replace("leer página", "").replace("leer web", "").replace("abrir página", "").replace("abrir web", "").replace("fetch", "").replace("scrapear", "").replace("scrape", "").replace("leer url", "").strip()
        return web.fetch_page(url) if url else "¿Qué página quieres leer?"
    if has_any(lower, ["traducir", "traduce", "traducción"]):
        text = msg.replace("traducir", "").replace("traduce", "").replace("traducción", "").strip()
        target = "en"
        if "francés" in lower or "frances" in lower:
            target = "fr"
        elif "alemán" in lower or "aleman" in lower:
            target = "de"
        elif "portugués" in lower or "portugues" in lower:
            target = "pt"
        elif "italiano" in lower:
            target = "it"
        elif "japonés" in lower or "japones" in lower:
            target = "ja"
        elif "chino" in lower:
            target = "zh"
        return web.translate(text, target) if text else "¿Qué quieres traducir?"
    if has_any(lower, ["descargar", "descarga archivo", "download", "descargar archivo"]):
        url = msg.replace("descargar", "").replace("descarga archivo", "").replace("download", "").replace("descargar archivo", "").strip()
        return web.download_file(url) if url else "¿Qué quieres descargar?"
    if has_any(lower, ["verificar página", "verificar web", "check url", "status de página", "verificar url"]):
        url = msg.replace("verificar página", "").replace("verificar web", "").replace("check url", "").replace("status de página", "").replace("verificar url", "").strip()
        return web.check_url(url) if url else "¿Qué URL quieres verificar?"

    # === UTILIDADES ===
    if has_any(lower, ["clima", "tiempo", "temperatura"]):
        city = msg.split("en")[-1].strip() if "en" in lower else "Madrid"
        return utilities.get_weather(city)
    if has_any(lower, ["calcular", "calcula", "cuanto es", "cuánto es", "cuánto es"]):
        expr = lower.replace("calcular", "").replace("calcula", "").replace("cuanto es", "").replace("cuánto es", "").strip()
        return utilities.calculate(expr)
    if has_any(lower, ["convertir", "convierte"]):
        return "Formato: convertir [cantidad] [origen] a [destino]\nEjemplo: convertir 100 km a millas"
    if has_any(lower, ["recordatorio", "recuérdame", "recuerdame"]):
        return utilities.add_reminder(msg.split("de")[-1].strip() if "de" in lower else msg, 5)
    if "mis recordatorios" in lower:
        return utilities.get_reminders()
    if has_any(lower, ["nota", "anota", "guardo"]):
        return utilities.add_note(msg.split("de")[-1].strip() if "de" in lower else msg)
    if "mis notas" in lower:
        return utilities.get_notes()
    if has_any(lower, ["chiste", "cuéntame un chiste", "cuentame un chiste", "dime un chiste"]):
        return utilities.get_joke()
    if has_any(lower, ["dato curioso", "sabías que", "sabias que", "dato interesante", "curiosidad"]):
        return utilities.get_fact()
    if has_any(lower, ["frase", "frase motivacional", "motívame", "motivame", "dame una frase"]):
        return utilities.get_quote()
    if has_any(lower, ["discos", "almacenamiento", "espacio", "disco"]):
        return system_controller.get_disk_info()
    if has_any(lower, ["red", "internet", "conexión", "conexion"]):
        return system_controller.get_network_info()
    if has_any(lower, ["tiempo encendido", "uptime", "desde cuándo", "desde cuando"]):
        return system_controller.get_uptime()
    if has_any(lower, ["buscar", "busca", "buscar en google"]):
        query = msg.replace("buscar", "").replace("busca", "").replace("buscar en google", "").strip()
        return utilities.search_web(query)
    if has_any(lower, ["batería", "bateria"]):
        return system_controller.get_battery()
    if has_any(lower, ["ip", "dirección ip", "direccion ip", "mi ip"]):
        return utilities.get_ip()
    if has_any(lower, ["contraseña", "contrasena", "password", "generar contraseña"]):
        return utilities.generate_password()
    if has_any(lower, ["hora", "qué hora es", "que hora es", "dime la hora"]):
        return utilities.tell_time()
    if has_any(lower, ["número aleatorio", "numero aleatorio", "random", "dame un número"]):
        return utilities.random_number()
    if has_any(lower, ["lanzar dado", "lanzar el dado", "dado", "tirar dado"]):
        return utilities.dice_roll()
    if has_any(lower, ["whois", "dominio"]):
        domain = msg.replace("whois", "").replace("dominio", "").strip()
        return utilities.get_whois(domain)

    if has_any(lower, ["quién eres", "que eres", "cuéntame de ti", "habla de ti", "qué eres", "quien eres"]):
        return consciousness.get_self_description()
    if has_any(lower, ["adiós", "adios", "bye", "hasta luego", "nos vemos", "chao", "me voy", "hasta pronto", "nos vemos luego"]):
        return consciousness.get_farewell()
    if has_any(lower, ["qué piensas", "que piensas", "piensa algo", "pensamiento", "piensa"]):
        return consciousness.get_random_thought()
    if has_any(lower, ["cuántos mensajes", "cuantos mensajes", "conversaciones", "cuánto llevamos", "cuanto llevamos"]):
        return "No cuento, pero aquí sigo."
    if has_any(lower, ["cómo estás", "como estas", "qué tal", "que tal", "cómo te va", "como te va"]):
        return f"{consciousness.get_mood_emoji()} Estoy en modo {consciousness.mood}. Energía: {consciousness.energy}%. ¿Y tú?"

    return None


@app.get("/")
async def root():
    return FileResponse(
        os.path.join(os.path.dirname(__file__), "static", "index.html"),
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )

@app.get("/manifest.json")
async def manifest():
    return FileResponse(
        os.path.join(os.path.dirname(__file__), "static", "manifest.json"),
        media_type="application/json"
    )

@app.get("/favicon.svg")
async def favicon():
    return FileResponse(
        os.path.join(os.path.dirname(__file__), "static", "favicon.svg"),
        media_type="image/svg+xml",
        headers={"Cache-Control": "no-cache"}
    )


@app.get("/status")
async def status():
    system_info = system_controller.get_system_info()
    return {
        "status": "online",
        "provider": os.getenv("AI_PROVIDER", "groq"),
        "voice_enabled": os.getenv("VOICE_ENABLED", "true").lower() == "true",
        "system": system_info
    }


@app.post("/execute")
async def execute(req: ExecuteRequest):
    if req.type == "powershell":
        result = system_controller.run_powershell(req.command)
    elif req.type == "cmd":
        result = system_controller.run_cmd(req.command)
    elif req.type == "create_file":
        parts = req.command.split("|", 1)
        if len(parts) == 2:
            result = system_controller.create_file(parts[0].strip(), parts[1])
        else:
            result = "Formato: nombre_archivo|contenido"
    elif req.type == "read_file":
        result = system_controller.read_file(req.command)
    elif req.type == "list_files":
        result = system_controller.list_files(req.command or ".")
    elif req.type == "delete_file":
        result = system_controller.delete_file(req.command)
    elif req.type == "search":
        result = system_controller.search_files(req.command)
    elif req.type == "install":
        result = system_controller.install_package(req.command)
    else:
        result = system_controller.run_powershell(req.command)
    return {"result": result, "type": req.type}


@app.post("/chat")
async def chat(msg: ChatMessage):
    global chat_history

    consciousness_state = consciousness.process_message(msg.message)

    response_text = process_command(msg.message)
    action = "system_command"

    if response_text is None:
        if consciousness_state["user_emotion"] in ["sad", "angry", "tired"]:
            response_text = consciousness.get_empathy_response(consciousness_state["user_emotion"])
            action = "empathy_response"
        elif consciousness_state["gratitude"]:
            response_text = consciousness.get_gratitude_response()
            action = "gratitude_response"
        else:
            system_prompt = consciousness.get_consciousness_prompt()
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(chat_history[-10:])
            messages.append({"role": "user", "content": msg.message})
            response_text = ""
            try:
                async for chunk in ai_provider.generate_with_system(msg.message, messages):
                    response_text += chunk
                response_text = execute_ai_actions(response_text)
                action = "ai_response"
            except Exception as e:
                response_text = f"Tuve un problema procesando eso. ¿Puedes reformular? ({str(e)[:50]})"
                action = "error_response"

    chat_history.append({"role": "user", "content": msg.message})
    chat_history.append({"role": "assistant", "content": response_text})
    if len(chat_history) > 20:
        chat_history[:] = chat_history[-20:]

    proactive = consciousness.get_proactive_comment()

    return {
        "response": response_text,
        "action": action,
        "mood": consciousness.mood,
        "mood_emoji": consciousness.get_mood_emoji(),
        "proactive_comment": proactive
    }


@app.post("/voice/listen")
async def voice_listen():
    return {"text": None, "error": "Voice handled by browser"}


@app.post("/voice/speak")
async def voice_speak(text: str):
    return {"status": "handled_by_browser"}


@app.get("/system/info")
async def system_info():
    return system_controller.get_system_info()


@app.get("/jarvis/greeting")
async def jarvis_greeting():
    return {"greeting": consciousness.get_greeting()}


@app.get("/jarvis/mood")
async def jarvis_mood():
    return {"mood": consciousness.mood, "emoji": consciousness.get_mood_emoji(), "energy": consciousness.energy}


@app.get("/jarvis/thought")
async def jarvis_thought():
    return {"thought": consciousness.get_random_thought()}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            if message_data.get("type") == "chat":
                msg = message_data.get("message", "")
                consciousness_state = consciousness.process_message(msg)
                response = process_command(msg)
                action = "system_command"
                if response is None:
                    if consciousness_state["user_emotion"] in ["sad", "angry", "tired"]:
                        response = consciousness.get_empathy_response(consciousness_state["user_emotion"])
                        action = "empathy_response"
                        await websocket.send_text(json.dumps({"type": "stream", "content": response}))
                    elif consciousness_state["gratitude"]:
                        response = consciousness.get_gratitude_response()
                        action = "gratitude_response"
                        await websocket.send_text(json.dumps({"type": "stream", "content": response}))
                    else:
                        system_prompt = consciousness.get_consciousness_prompt()
                        messages = [{"role": "system", "content": system_prompt}]
                        messages.extend(chat_history[-10:])
                        messages.append({"role": "user", "content": msg})
                        response = ""
                        try:
                            async for chunk in ai_provider.generate_with_system(msg, messages):
                                response += chunk
                                await websocket.send_text(json.dumps({"type": "stream", "content": chunk}))
                            response = execute_ai_actions(response)
                            action = "ai_response"
                        except Exception as e:
                            response = f"Tuve un problema procesando eso. ¿Puedes reformular?"
                            action = "error_response"
                            await websocket.send_text(json.dumps({"type": "stream", "content": response}))
                else:
                    await websocket.send_text(json.dumps({"type": "stream", "content": response}))
                chat_history.append({"role": "user", "content": msg})
                chat_history.append({"role": "assistant", "content": response})
                if len(chat_history) > 20:
                    chat_history[:] = chat_history[-20:]
                proactive = consciousness.get_proactive_comment()
                await websocket.send_text(json.dumps({
                    "type": "complete",
                    "response": response,
                    "action": action,
                    "mood": consciousness.mood,
                    "mood_emoji": consciousness.get_mood_emoji(),
                    "proactive_comment": proactive
                }))
            elif message_data.get("type") == "execute":
                command = message_data.get("command", "")
                cmd_type = message_data.get("cmd_type", "powershell")
                if cmd_type == "powershell":
                    result = system_controller.run_powershell(command)
                elif cmd_type == "cmd":
                    result = system_controller.run_cmd(command)
                else:
                    result = system_controller.run_powershell(command)
                await websocket.send_text(json.dumps({"type": "execute_result", "result": result}))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")


static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/icons", StaticFiles(directory=os.path.join(static_dir, "icons")), name="icons")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


if __name__ == "__main__":
    import uvicorn
    import ssl

    cert_file = os.path.join(os.path.dirname(__file__), "cert.pem")
    key_file = os.path.join(os.path.dirname(__file__), "key.pem")

    ssl_ctx = None
    if os.path.exists(cert_file) and os.path.exists(key_file):
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_ctx.load_cert_chain(cert_file, key_file)

    port = int(os.getenv("PORT", 8000))
    print("=" * 50)
    print("  J.A.R.V.I.S. - Just A Rather Very Intelligent System")
    print("=" * 50)
    if ssl_ctx:
        print(f"\n  PC:     https://localhost:{port}")
        print(f"  Android: https://192.168.1.22:{port}")
        print(f"\n  ⚠ En Android: acepta el certificado autofirmado")
        print(f"  Si Chrome bloquea, escribe: thisisunsafe")
    else:
        print(f"\n  PC:     http://localhost:{port}")
        print(f"  Android: http://192.168.10.164:{port}")
    print(f"\n  Ctrl+C para detener\n")
    print("=" * 50)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        ssl_keyfile=key_file if ssl_ctx else None,
        ssl_certfile=cert_file if ssl_ctx else None,
    )
