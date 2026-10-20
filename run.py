import sys, os
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import socket
import uvicorn
import webbrowser
import time
import threading

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(0.5)
            s.connect((host, port))
            return True
        except (OSError, ConnectionRefusedError):
            return False

def open_browser(port: int):
    time.sleep(1.5)
    url = f"http://localhost:{port}"
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Browser launch note: {e}")

def run_port_8000():
    try:
        uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, log_level="warning")
    except Exception as e:
        pass

if __name__ == "__main__":
    print("=" * 65)
    print("🛸 FLYING CABS PLATFORM — NEXT-GEN AERO MOBILITY (BHARAT EDITION)")
    print("=" * 65)
    print("Starting FastAPI ASGI Server with WebSockets & REST API...")
    print("Web UI (Primary):       http://localhost:3000   (or http://127.0.0.1:3000)")
    print("Web UI (Compatibility):  http://localhost:8000   (or http://127.0.0.1:8000)")
    print("API Documentation:      http://localhost:3000/docs")
    print("Health Check:           http://localhost:3000/health")
    print("=" * 65)

    primary_port = 3000
    if is_port_in_use(3000):
        if not is_port_in_use(8000):
            primary_port = 8000
            print("Port 3000 is occupied; using Port 8000 as primary.")
        else:
            primary_port = 3001
            print(f"Ports 3000 and 8000 are occupied; using Port {primary_port} as primary.")

    # Run port 8000 in background if primary is 3000 and 8000 is available
    if primary_port == 3000 and not is_port_in_use(8000):
        threading.Thread(target=run_port_8000, daemon=True).start()

    # Auto-launch default browser directly to primary UI
    threading.Thread(target=open_browser, args=(primary_port,), daemon=True).start()

    # Run primary port on 0.0.0.0
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=primary_port, reload=False, log_level="info")
