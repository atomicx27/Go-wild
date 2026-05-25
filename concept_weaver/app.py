import http.server
import socketserver
import json
import urllib.request
import urllib.error
import os

PORT = 8000
OLLAMA_URL = "http://localhost:11434"

def get_available_model():
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode('utf-8'))
            models = data.get('models', [])
            if models:
                # Prioritize llama3 if it exists, otherwise take the first
                model_names = [m['name'] for m in models]
                for name in model_names:
                    if 'llama3' in name:
                        return name
                return model_names[0]
    except Exception as e:
        print(f"Warning: Could not fetch models from Ollama: {e}")
    return "llama3"

class WeaverHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/weave':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode('utf-8'))
                topic = data.get('topic', '')

                if not topic:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'{"error": "Topic is required"}')
                    return

                model = get_available_model()
                print(f"Using model: {model} for topic: {topic}")

                system_prompt = """
You are an expert knowledge architect. Deconstruct the given topic into a knowledge graph.
Output strictly valid JSON with the following structure:
{
    "nodes": [
        {"id": 1, "label": "Node Name", "title": "Detailed description of the node, explaining its significance."}
    ],
    "edges": [
        {"from": 1, "to": 2, "label": "relationship description"}
    ]
}
Provide 10-15 nodes that cover the core concepts, history, applications, or key figures related to the topic. Connect them logically with edges.
Make sure the root concept is node 1.
"""

                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Deconstruct the following topic: {topic}"}
                    ],
                    "format": "json",
                    "stream": False
                }

                req = urllib.request.Request(f"{OLLAMA_URL}/api/chat", data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=120) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    response_message = result.get('message', {}).get('content', '{}')

                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(response_message.encode('utf-8'))

            except Exception as e:
                print(f"Error connecting to Ollama: {e}. Falling back to mock data.")
                # Graceful fallback to mock data for demonstration
                mock_data = {
                    "nodes": [
                        {"id": 1, "label": topic, "title": f"The main concept: {topic}"},
                        {"id": 2, "label": "History", "title": f"The history of {topic}"},
                        {"id": 3, "label": "Applications", "title": f"Real-world applications of {topic}"},
                        {"id": 4, "label": "Future", "title": f"The future trajectory of {topic}"}
                    ],
                    "edges": [
                        {"from": 1, "to": 2, "label": "has"},
                        {"from": 1, "to": 3, "label": "used in"},
                        {"from": 1, "to": 4, "label": "leads to"}
                    ]
                }
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(mock_data).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Not Found"}')

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    # Change to the directory containing app.py so SimpleHTTPRequestHandler serves files from here
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # allow address reuse
    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer(("", PORT), WeaverHandler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()
