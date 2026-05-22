import http.server
import socketserver
import json
import os
import urllib.parse
from . import indexer
from . import llm

PORT = 8080
DIRECTORY = os.path.join(os.path.dirname(__file__), "static")

class OracleRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                req_data = json.loads(post_data.decode('utf-8'))
                query = req_data.get('query', '')
                use_rag = req_data.get('use_rag', True)

                context = ""
                snippets = []

                if use_rag:
                    print(f"Searching codebase for: {query}")
                    results = indexer.search_codebase(query, limit=5)

                    if results:
                        context = "Context from codebase:\n"
                        for res in results:
                            snippets.append(res['filepath'])
                            context += f"--- {res['filepath']} ---\n{res['content']}\n\n"
                    else:
                        context = "No relevant code snippets found in the codebase.\n"

                system_prompt = (
                    "You are the Code Oracle, a highly advanced AI assistant integrated into a local repository. "
                    "Use the provided context to answer the user's questions about the code. "
                    "If the context doesn't contain the answer, use your general programming knowledge but mention it's not in the retrieved context. "
                    "Provide clear, concise, and helpful answers."
                )

                full_prompt = f"{context}\nUser Query: {query}"

                # We'll stream the response back using chunked transfer encoding
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Transfer-Encoding', 'chunked')
                self.end_headers()

                # First, send the snippets we found
                init_data = json.dumps({"type": "snippets", "data": list(set(snippets))})
                self._send_chunk(init_data)

                # Then stream the LLM response
                for chunk in llm.generate_stream(full_prompt, system=system_prompt):
                    # We wrap each piece of text in a JSON object to easily parse on client
                    chunk_data = json.dumps({"type": "text", "data": chunk})
                    self._send_chunk(chunk_data)

                # Send done signal
                done_data = json.dumps({"type": "done"})
                self._send_chunk(done_data)

                self._send_chunk("") # Empty chunk to finish

            except Exception as e:
                print(f"Error handling request: {e}")
                self.send_error(500, f"Internal Server Error: {e}")
        else:
            self.send_error(404, "Not Found")

    def _send_chunk(self, data):
        """Sends a chunk in HTTP chunked transfer encoding format"""
        if not data:
            chunk = b"0\r\n\r\n"
        else:
            encoded_data = data.encode('utf-8') + b"\n"
            chunk = f"{len(encoded_data):X}\r\n".encode('utf-8') + encoded_data + b"\r\n"
        self.wfile.write(chunk)
        self.wfile.flush()

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), OracleRequestHandler) as httpd:
        print(f"Oracle Server running at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")

if __name__ == "__main__":
    run_server()
