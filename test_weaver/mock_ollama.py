import http.server
import json
import socketserver

PORT = 11434

request_count = 0

class MockOllamaHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        global request_count
        if self.path == '/api/generate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            request_count += 1

            if request_count == 1:
                # First attempt: return tests that intentionally fail
                test_code = """
import pytest
from dummy_math import add, divide, complex_operation

def test_add():
    assert add(2, 3) == 6  # Intentional error here

def test_divide():
    assert divide(10, 2) == 5

def test_complex():
    assert complex_operation(-1) == 0
"""
                response_data = {
                    "model": data.get("model", "llama3"),
                    "response": f"Here are the tests:\n```python\n{test_code}\n```",
                    "done": True
                }
            else:
                # Second attempt: return corrected tests
                test_code = """
import pytest
from dummy_math import add, divide, complex_operation

def test_add():
    assert add(2, 3) == 5  # Fixed

def test_divide():
    assert divide(10, 2) == 5

def test_complex():
    assert complex_operation(-1) == 0
"""
                response_data = {
                    "model": data.get("model", "llama3"),
                    "response": f"I have corrected the tests:\n```python\n{test_code}\n```",
                    "done": True
                }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), MockOllamaHandler) as httpd:
        print(f"Serving mock Ollama at port {PORT}")
        httpd.serve_forever()
