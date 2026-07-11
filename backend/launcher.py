import os
import sys
import webbrowser
import threading
import time

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_resource_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS)
    return os.path.dirname(os.path.abspath(__file__))

base_path = get_base_path()
resource_path = get_resource_path()

os.environ.setdefault("PORT", "8000")
os.environ.setdefault("AI_PROVIDER", "groq")

from dotenv import load_dotenv
env_path = os.path.join(base_path, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

def open_browser():
    time.sleep(2)
    webbrowser.open("https://localhost:8000")

if __name__ == "__main__":
    sys.path.insert(0, resource_path)
    os.chdir(resource_path)

    import uvicorn
    import ssl

    cert_file = os.path.join(resource_path, "cert.pem")
    key_file = os.path.join(resource_path, "key.pem")

    ssl_ctx = None
    if os.path.exists(cert_file) and os.path.exists(key_file):
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_ctx.load_cert_chain(cert_file, key_file)

    port = int(os.getenv("PORT", 8000))

    print("=" * 50)
    print("  J.A.R.V.I.S. - Just A Rather Very Intelligent System")
    print("=" * 50)
    print(f"\n  Abre en tu navegador: https://localhost:{port}")
    print(f"  Presiona Ctrl+C para detener\n")
    print("=" * 50)

    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        ssl_keyfile=key_file if ssl_ctx else None,
        ssl_certfile=cert_file if ssl_ctx else None,
        reload=False,
    )
