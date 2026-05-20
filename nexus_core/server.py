import http.server
import socketserver
import json
import os
import threading
from urllib.parse import urlparse, parse_qs
from .agent import NexusAgent

PORT = 8000
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')

# Global state for simple demonstration
agent_logs = []
agent_instance = None
agent_thread = None

def append_log(log_entry):
    agent_logs.append(log_entry)
    # Keep last 100 logs
    if len(agent_logs) > 100:
        agent_logs.pop(0)

class APIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = {
                "running": agent_instance is not None and agent_instance.is_running,
                "ollama_available": NexusAgent().check_ollama()
            }
            self.wfile.write(json.dumps(status).encode())
            return

        if parsed_path.path == '/api/logs':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(agent_logs).encode())
            return

        # Serve static files for all other GET requests
        super().do_GET()

    def do_POST(self):
        global agent_instance, agent_thread, agent_logs
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/api/task':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            task = data.get("task", "")

            if not task:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Task is required"}')
                return

            if agent_instance and agent_instance.is_running:
                self.send_response(409)
                self.end_headers()
                self.wfile.write(b'{"error": "Agent is already running a task"}')
                return

            agent_logs.clear()
            agent_instance = NexusAgent(log_callback=append_log)
            agent_thread = threading.Thread(target=agent_instance.run, args=(task,))
            agent_thread.start()

            self.send_response(202)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Task accepted"}).encode())
            return

        self.send_response(404)
        self.end_headers()

def run_server():
    with socketserver.TCPServer(("", PORT), APIHandler) as httpd:
        print(f"Nexus Core Server running at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")

if __name__ == "__main__":
    run_server()
