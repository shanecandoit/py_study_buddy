import threading
import time
import uvicorn
import webview
import os
import http.server
import socketserver
from backend.main import app as backend_app  # Import the FastAPI app from backend/main.py

def run_backend():
    try:
        print("Running backend server...")
        uvicorn.run(backend_app, host="0.0.0.0", port=8000)  # Run the imported app, removed reload
    except Exception as e:
        print(f"Backend failed with error: {e}")

# Frontend setup
# TODO clean this up
def run_frontend_server():
    try:
        os.chdir("frontend")  # Change to frontend directory
        PORT = 8080
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Serving frontend at port {PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"Frontend server failed with error: {e}")

def load_frontend():
    webview.create_window("Study Buddy", "http://localhost:8080/index.html")
    webview.start(debug=True)


if __name__ == "__main__":
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend)
    backend_thread.daemon = True
    backend_thread.start()

    # Start frontend server in a separate thread
    frontend_server_thread = threading.Thread(target=run_frontend_server)
    frontend_server_thread.daemon = True
    frontend_server_thread.start()

    # Give the backend and frontend servers a moment to start
    time.sleep(2)

    # Load the frontend in the main thread
    load_frontend()