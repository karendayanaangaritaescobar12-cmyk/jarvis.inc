import os
import json
import re
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

from ai_providers import get_provider
from system_control import system_controller
from utilities import utilities
from consciousness import consciousness
from web_access import web
from chat_store import chat_store
from intent_router import intent_router, Intent
from semantic_memory import semantic_memory
from learning import learning
from summarizer import summarizer
from spotify_api import spotify_api
from google_services import google_services
from vision import vision
from task_executor import task_executor
from natural_voice import natural_voice

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


class ChatMessage(BaseModel):
    message: str
    voice: bool = False


class ExecuteRequest(BaseModel):
    command: str
    type: str = "powershell"


def execute_ai_actions(text: str) -> str:
    patterns = {
        'EXEC': (r'\[EXEC:\s*(.+?)\]', 'exec'),
        'CREATE': (r'\[CREATE:\s*(.+?)\]\n(.*?)(?=\[|\Z)', 'create'),
        'READ': (r'\[READ:\s*(.+?)\]', 'read'),
        'INSTALL': (r'\[INSTALL:\s*(.+?)\]', 'install'),
        'OPEN': (r'\[OPEN:\s*(.+?)\]', 'open'),
        'SEARCH': (r'\[SEARCH:\s*(.+?)\]', 'search'),
    }
    results = []
    for tag, (pattern, action) in patterns.items():
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            if action == 'exec':
                cmd = match.strip()
                output = system_controller.run_powershell(cmd) if not any(
                    x in cmd.lower() for x in ["pip ", "npm ", "apt ", "winget "]
                ) else system_controller.run_cmd(cmd)
                results.append(f"[{cmd}]:\n{output}")
            elif action == 'create':
                fname = match[0].strip() if isinstance(match, tuple) else match.strip()
                content = match[1].strip() if isinstance(match, tuple) and len(match) > 1 else ""
                output = system_controller.create_file(fname, content)
                results.append(output)
            elif action == 'read':
                output = system_controller.read_file(match.strip())
                results.append(f"Contenido de {match.strip()}:\n{output}")
            elif action == 'install':
                output = system_controller.install_package(match.strip())
                results.append(output)
            elif action == 'open':
                output = system_controller.open_app(match.strip())
                results.append(output)
            elif action == 'search':
                output = system_controller.search_file_content(match.strip())
                results.append(output)
    for pattern, _ in patterns.values():
        text = re.sub(pattern, '', text, flags=re.DOTALL).strip()
    if results:
        text += "\n\n" + "\n".join(results)
    return text


async def handle_intent(intent: Intent, original_msg: str) -> Optional[str]:
    name = intent.name
    ent = intent.entities

    if name == "spotify_play":
        query = ent.get("query", "").strip()
        if query:
            return system_controller.spotify_search_and_play(query)
        return system_controller.open_spotify()
    if name == "spotify_next":
        return system_controller.spotify_next()
    if name == "spotify_prev":
        return system_controller.spotify_prev()
    if name == "spotify_pause":
        return system_controller.spotify_play_pause()
    if name == "spotify_open":
        return system_controller.open_spotify()
    if name == "spotify_artist":
        return system_controller.spotify_open_artist(ent.get("artist", ""))
    if name == "spotify_playlist":
        return system_controller.spotify_open_playlist(ent.get("playlist", ""))

    if name == "volume_up":
        return system_controller.change_volume("up")
    if name == "volume_down":
        return system_controller.change_volume("down")
    if name == "mute":
        return system_controller.mute_volume()

    if name == "open_browser":
        if "firefox" in original_msg.lower():
            return system_controller.open_app("firefox")
        if "edge" in original_msg.lower():
            return system_controller.open_app("edge")
        return system_controller.open_browser()
    if name == "open_calculator":
        return system_controller.open_calculator()
    if name == "open_explorer":
        return system_controller.open_explorer()
    if name == "open_vscode":
        return system_controller.open_vscode()
    if name == "open_app":
        return system_controller.open_app(ent.get("app_name", ""))
    if name == "open_any_app":
        return system_controller.open_app(ent.get("app_name", ""))
    if name == "close_app":
        return system_controller.close_app(ent.get("app_name", ""))

    if name == "shutdown":
        return system_controller.shutdown()
    if name == "restart":
        return system_controller.restart()
    if name == "lock":
        return system_controller.lock_screen()
    if name == "processes":
        return system_controller.get_running_processes()
    if name == "system_info":
        info = system_controller.get_system_info()
        bat = info.get('battery')
        bat_str = f"\nBatería: {bat['percent']}% ({'Cargando' if bat['power_plugged'] else 'Sin carga'})" if bat else ""
        return f"Sistema: {info['system']} {info['version']}\nCPU: {info['cpu_percent']}%\nMemoria: {info['memory']['percent']}%{bat_str}"
    if name == "minimize":
        return system_controller.minimize_window()
    if name == "maximize":
        return system_controller.maximize_window()
    if name == "screenshot":
        result = vision.take_screenshot()
        return result or "No pude tomar la captura."

    if name == "clipboard_copy":
        return system_controller.set_clipboard(ent.get("text", ""))
    if name == "clipboard_paste":
        return system_controller.get_clipboard()

    if name == "file_create":
        parts = ent.get("filename", "")
        if "|" in parts:
            fname, content = parts.split("|", 1)
            return system_controller.create_file(fname.strip(), content.strip())
        import re as _re
        m = _re.search(r'(\S+\.\w+)', parts)
        if m:
            fname = m.group(1)
            rest = parts[m.end():].strip()
            if rest.startswith("con "):
                rest = rest[4:].strip()
            content = rest if rest else ""
            return system_controller.create_file(fname, content)
        return system_controller.create_file(parts, "")
    if name == "folder_create":
        return system_controller.create_directory(ent.get("foldername", ""))
    if name == "file_read":
        raw_path = ent.get("filename", "")
        raw_path = re.sub(r'^(?:el|la|los|las|del|de)\s+', '', raw_path, flags=re.IGNORECASE).strip()
        return system_controller.read_file(raw_path)
    if name == "file_edit":
        parts = ent.get("args", "")
        if "|" in parts:
            path, rest = parts.split("|", 1)
            if "|" in rest:
                old_text, new_text = rest.split("|", 1)
                return system_controller.edit_file(path.strip(), old_text.strip(), new_text.strip())
        return "Formato: editar archivo [nombre] | [texto viejo] | [texto nuevo]"
    if name == "file_delete":
        return system_controller.delete_file(ent.get("filename", ""))
    if name == "file_list":
        raw_path = ent.get("path", ".") or "."
        raw_path = re.sub(r'^(en|de|del|la|el|las|los)\s+', '', raw_path, flags=re.IGNORECASE).strip()
        return system_controller.list_files(raw_path or ".")
    if name == "file_search":
        return system_controller.search_file_content(ent.get("pattern", ""))
    if name == "file_move":
        return system_controller.move_file(ent.get("source", ""), ent.get("dest", ""))
    if name == "file_copy":
        return system_controller.copy_file(ent.get("source", ""), ent.get("dest", ""))
    if name == "file_append":
        return system_controller.append_file(ent.get("filename", ""), ent.get("content", ""))
    if name == "file_rename":
        return system_controller.rename_file(ent.get("old_name", ""), ent.get("new_name", ""))
    if name == "file_info":
        return system_controller.file_info(ent.get("path", ".") or ".")
    if name == "file_tree":
        return system_controller.tree_view(ent.get("path", ".") or ".")

    if name in ["task_organize", "task_script", "task_backup", "task_project", "task_cleanup"]:
        return await task_executor.execute_task(ent.get("description", ""), system_controller, ai_provider)

    if name == "web_search":
        return web.search_google(ent.get("query", ""))
    if name == "news":
        return web.get_news(ent.get("topic", "general") or "general")
    if name == "weather":
        return web.get_weather(ent.get("city", "Madrid") or "Madrid")
    if name == "define":
        return web.get_wikipedia(ent.get("word", ""))
    if name == "wikipedia":
        return web.get_wikipedia(ent.get("query", ""))
    if name == "fetch_page":
        return web.fetch_page(ent.get("url", ""))
    if name == "translate":
        text = ent.get("text", "")
        target = ent.get("target", "en") or "en"
        lang_map = {"francés": "fr", "frances": "fr", "alemán": "de", "aleman": "de",
                     "portugués": "pt", "portugues": "pt", "italiano": "it", "japonés": "ja", "chino": "zh"}
        for k, v in lang_map.items():
            if k in original_msg.lower():
                target = v
                break
        return web.translate(text, target) if text else "¿Qué quieres traducir?"
    if name == "download":
        return web.download_file(ent.get("url", ""))

    if name == "calculate":
        return utilities.calculate(ent.get("expression", ""))
    if name == "reminder":
        return utilities.add_reminder(ent.get("text", ""), 5)
    if name == "note_add":
        return utilities.add_note(ent.get("text", ""))
    if name == "joke":
        return utilities.get_joke()
    if name == "fact":
        return utilities.get_fact()
    if name == "quote":
        return utilities.get_quote()
    if name == "time":
        return utilities.tell_time()
    if name == "password":
        return utilities.generate_password()
    if name == "ip":
        return utilities.get_ip()
    if name == "battery":
        return system_controller.get_battery()
    if name == "disk_info":
        return system_controller.get_disk_info()
    if name == "network_info":
        return system_controller.get_network_info()
    if name == "uptime":
        return system_controller.get_uptime()

    if name == "system_review":
        return system_controller.system_review()
    if name == "installed_programs":
        return system_controller.list_installed_programs()
    if name == "services":
        return system_controller.list_services()
    if name == "drivers":
        return system_controller.list_drivers()
    if name == "env_vars":
        return system_controller.list_environment_paths()
    if name == "gpu":
        return system_controller.gpu_info()
    if name == "temperature":
        return system_controller.temperature_info()
    if name == "firewall":
        return system_controller.firewall_status()
    if name == "processes_detailed":
        return system_controller.detailed_processes()

    if name == "who_greeting":
        return consciousness.get_self_description()
    if name == "farewell":
        return consciousness.get_farewell()
    if name == "thought":
        return consciousness.get_random_thought()
    if name == "mood_check":
        return f"{consciousness.get_mood_emoji()} Estoy en modo {consciousness.mood}. Energía: {consciousness.energy}%."

    return None


async def process_ai_chat(msg: str) -> tuple:
    system_prompt = consciousness.get_consciousness_prompt()
    user_context = learning.get_user_context()
    semantic_context = semantic_memory.get_context_for_query(msg)

    if semantic_context:
        system_prompt += f"\n\n{semantic_context}"
    if user_context:
        system_prompt += f"\n\n{user_context}"

    context = chat_store.get_context(limit=50)
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(context)
    messages.append({"role": "user", "content": msg})

    response_text = ""
    async for chunk in ai_provider.generate_with_system(msg, messages):
        response_text += chunk

    response_text = execute_ai_actions(response_text)
    return response_text, "ai_response"


async def handle_chat_message(msg: str) -> dict:
    consciousness_state = consciousness.process_message(msg)

    intent = intent_router.classify(msg)
    if intent:
        result = await handle_intent(intent, msg)
        if result:
            chat_store.add_message("user", msg)
            chat_store.add_message("assistant", result)
            learning.learn_from_message(msg, result)
            return {
                "response": result,
                "action": "system_command",
                "mood": consciousness.mood,
                "mood_emoji": consciousness.get_mood_emoji(),
                "proactive_comment": consciousness.get_proactive_comment()
            }

    if consciousness_state["user_emotion"] in ["sad", "angry", "tired"]:
        response = consciousness.get_empathy_response(consciousness_state["user_emotion"])
        action = "empathy_response"
    elif consciousness_state["gratitude"]:
        response = consciousness.get_gratitude_response()
        action = "gratitude_response"
    else:
        try:
            response, action = await process_ai_chat(msg)
        except Exception as e:
            response = f"Tuve un problema procesando eso. ¿Puedes reformular? ({str(e)[:50]})"
            action = "error_response"

    chat_store.add_message("user", msg)
    chat_store.add_message("assistant", response)
    learning.learn_from_message(msg, response)
    semantic_memory.add_conversation_memory(msg, response)

    if len(chat_store.history) >= summarizer.summary_threshold:
        recent = chat_store.get_recent_without_summary(30)
        if len(recent) >= 15:
            summary = await summarizer.summarize_conversation(recent, ai_provider)
            if summary and not summary.startswith("No"):
                chat_store.add_summary(summary, f"last_{len(recent)}")

    return {
        "response": response,
        "action": action,
        "mood": consciousness.mood,
        "mood_emoji": consciousness.get_mood_emoji(),
        "proactive_comment": consciousness.get_proactive_comment()
    }


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
        "system": system_info,
        "features": {
            "semantic_memory": True,
            "persistent_history": True,
            "learning": True,
            "spotify_api": spotify_api.is_available(),
            "google_services": google_services.is_available(),
        }
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
        result = system_controller.search_file_content(req.command)
    elif req.type == "install":
        result = system_controller.install_package(req.command)
    else:
        result = system_controller.run_powershell(req.command)
    return {"result": result, "type": req.type}


@app.post("/chat")
async def chat(msg: ChatMessage):
    result = await handle_chat_message(msg.message)
    return result


@app.post("/upload")
async def upload_file(file: UploadFile = File(...), path: str = ""):
    try:
        content = await file.read()
        if path:
            save_path = path
        else:
            save_path = os.path.join(system_controller.workspace, file.filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(content)
        size_kb = len(content) / 1024
        return {"result": f"Archivo guardado: {save_path} ({size_kb:.1f} KB)", "path": save_path}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/jarvis/greeting")
async def jarvis_greeting():
    return {"greeting": consciousness.get_greeting()}

@app.get("/jarvis/mood")
async def jarvis_mood():
    return {"mood": consciousness.mood, "emoji": consciousness.get_mood_emoji(), "energy": consciousness.energy}

@app.get("/jarvis/thought")
async def jarvis_thought():
    return {"thought": consciousness.get_random_thought()}

@app.get("/jarvis/history")
async def jarvis_history():
    return {"history": chat_store.get_all()[-100:]}

@app.get("/jarvis/favorites")
async def jarvis_favorites():
    fav_file = os.path.join(os.path.dirname(__file__), "data", "favorites.json")
    if os.path.exists(fav_file):
        with open(fav_file, "r", encoding="utf-8") as f:
            return {"favorites": json.load(f)}
    return {"favorites": []}

class FavoritesRequest(BaseModel):
    favorites: list


@app.post("/jarvis/favorites")
async def save_favorites(req: FavoritesRequest):
    fav_file = os.path.join(os.path.dirname(__file__), "data", "favorites.json")
    os.makedirs(os.path.dirname(fav_file), exist_ok=True)
    with open(fav_file, "w", encoding="utf-8") as f:
        json.dump(req.favorites, f, ensure_ascii=False)
    return {"status": "ok"}

@app.get("/jarvis/memory")
async def jarvis_memory():
    return {"profile": learning.get_profile_summary(), "stats": chat_store.get_stats()}

@app.get("/jarvis/spotify/search/{query}")
async def spotify_search(query: str):
    return {"result": await spotify_api.search(query)}

@app.get("/jarvis/spotify/artist/{name}")
async def spotify_artist(name: str):
    return {"result": await spotify_api.get_artist_top_tracks(name)}

@app.get("/jarvis/calendar")
async def calendar_events():
    return {"result": await google_services.get_calendar_events()}

@app.get("/jarvis/gmail")
async def gmail_messages():
    return {"result": await google_services.get_gmail_messages()}

@app.get("/jarvis/memory/search/{query}")
async def memory_search(query: str):
    return {"results": semantic_memory.search(query)}

@app.get("/jarvis/screenshots")
async def screenshots_list():
    return {"result": vision.list_screenshots()}

@app.post("/jarvis/tts")
async def text_to_speech(text: str):
    audio_bytes = await natural_voice.text_to_audio_bytes(text)
    if audio_bytes:
        from fastapi.responses import Response
        return Response(content=audio_bytes, media_type="audio/mpeg")
    return {"error": "TTS not available"}

@app.get("/jarvis/tts/voices")
async def tts_voices():
    return {"voices": natural_voice.get_voices()}

@app.post("/jarvis/screenshot/analyze")
async def analyze_screenshot():
    filepath = await vision.take_screenshot()
    if not filepath:
        return {"error": "No pude tomar la captura"}
    try:
        with open(filepath, "rb") as f:
            import base64
            img_b64 = base64.b64encode(f.read()).decode()
        system_prompt = "Describe brevemente lo que ves en esta captura de pantalla. ¿Qué aplicaciones están abiertas? ¿Qué hay visible? Sé conciso."
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"[Imagen captura de pantalla guardada en: {filepath}]"}]
        response = ""
        async for chunk in ai_provider.generate_with_system("Describe esta captura de pantalla", messages):
            response += chunk
        return {"analysis": response, "screenshot": filepath}
    except Exception as e:
        return {"error": str(e)[:100]}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            if message_data.get("type") == "chat":
                msg = message_data.get("message", "")
                result = await handle_chat_message(msg)
                await websocket.send_text(json.dumps({
                    "type": "complete",
                    **result
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
        print(f"\n  Features: Semantic Memory | Learning | Spotify API | Calendar | Gmail")
    else:
        print(f"\n  PC:     http://localhost:{port}")
    print(f"\n  Ctrl+C para detener\n")
    print("=" * 50)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        ssl_keyfile=key_file if ssl_ctx else None,
        ssl_certfile=cert_file if ssl_ctx else None,
    )
