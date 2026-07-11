import os
import sys
import subprocess
import time
import signal

PYTHON = r"C:\Users\Kimet\AppData\Local\Programs\Python\Python311\python.exe"
BACKEND = os.path.join(os.path.dirname(__file__), "..", "backend")
MAIN_PY = os.path.join(BACKEND, "main.py")
PORT = 8000

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def is_running():
    try:
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        return f":{PORT}" in result.stdout and "LISTENING" in result.stdout
    except:
        return False

def get_pid():
    try:
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        for line in result.stdout.split('\n'):
            if f":{PORT}" in line and "LISTENING" in line:
                return line.split()[-1]
    except:
        pass
    return None

def start_server():
    if is_running():
        print(f"\n  [WARNING] Server already running on port {PORT}")
        print(f"  Access at: https://localhost:{PORT}")
        return
    
    print(f"\n  [INFO] Starting JARVIS server...")
    print(f"  [INFO] PC: https://localhost:{PORT}")
    print(f"  [INFO] Android: https://192.168.1.22:{PORT}")
    
    subprocess.Popen(
        [PYTHON, MAIN_PY],
        cwd=BACKEND,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    
    time.sleep(2)
    
    if is_running():
        print(f"\n  [OK] Server started successfully!")
    else:
        print(f"\n  [ERROR] Failed to start server")

def stop_server():
    pid = get_pid()
    if pid:
        print(f"\n  [INFO] Stopping server (PID: {pid})...")
        subprocess.run(['taskkill', '/PID', pid, '/F'], 
                      capture_output=True, 
                      creationflags=subprocess.CREATE_NO_WINDOW)
        time.sleep(1)
        print(f"  [OK] Server stopped")
    else:
        print(f"\n  [INFO] No server running on port {PORT}")

def show_status():
    if is_running():
        pid = get_pid()
        print(f"\n  [STATUS] Server RUNNING (PID: {pid})")
        print(f"  [URL] https://localhost:{PORT}")
        print(f"  [URL] https://192.168.1.22:{PORT}")
    else:
        print(f"\n  [STATUS] Server STOPPED")

def show_menu():
    clear()
    print("""
    ╔══════════════════════════════════════════╗
    ║     J.A.R.V.I.S. Server Manager         ║
    ║     Just A Rather Very Intelligent      ║
    ║              System                      ║
    ╚══════════════════════════════════════════╝
    """)
    show_status()
    print("""
    ┌────────────────────────────────────────┐
    │  [1] Start Server                      │
    │  [2] Stop Server                       │
    │  [3] Restart Server                    │
    │  [4] Open in Browser                   │
    │  [5] Install Auto-Start (Admin)        │
    │  [6] Uninstall Auto-Start (Admin)      │
    │  [0] Exit                              │
    └────────────────────────────────────────┘
    """)

def open_browser():
    import webbrowser
    webbrowser.open(f"https://localhost:{PORT}")
    print(f"\n  [INFO] Opening browser...")

def install_autostart():
    print(f"\n  [INFO] Opening installer (Run as Admin)...")
    bat = os.path.join(os.path.dirname(__file__), "install.bat")
    subprocess.run(['cmd', '/c', 'start', '', bat])

def uninstall_autostart():
    print(f"\n  [INFO] Opening uninstaller (Run as Admin)...")
    bat = os.path.join(os.path.dirname(__file__), "uninstall.bat")
    subprocess.run(['cmd', '/c', 'start', '', bat])

def main():
    while True:
        show_menu()
        choice = input("    Select option: ").strip()
        
        if choice == "1":
            start_server()
        elif choice == "2":
            stop_server()
        elif choice == "3":
            stop_server()
            time.sleep(1)
            start_server()
        elif choice == "4":
            open_browser()
        elif choice == "5":
            install_autostart()
        elif choice == "6":
            uninstall_autostart()
        elif choice == "0":
            print("\n  Goodbye!\n")
            sys.exit(0)
        else:
            print("\n  [ERROR] Invalid option")
        
        input("\n  Press Enter to continue...")

if __name__ == "__main__":
    main()
