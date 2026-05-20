import os
import sys
import argparse
import http.server
import socketserver
from builder import build_city

def start_server(port, public_dir):
    os.chdir(public_dir)
    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"\nNeural matrix interface online.")
        print(f"Access Code Metropolis at: http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down Matrix...")
            httpd.server_close()

def main():
    parser = argparse.ArgumentParser(description="Code Metropolis: Autonomous Codebase Visualization")
    parser.add_argument('target_dir', nargs='?', default='.', help="The directory to analyze (defaults to current dir)")
    parser.add_argument('--port', type=int, default=8000, help="Port for the local web server")

    args = parser.parse_args()

    target_dir = os.path.abspath(args.target_dir)
    print(f"Target Directory: {target_dir}")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    public_dir = os.path.join(script_dir, "public")
    output_file = os.path.join(public_dir, "city_data.json")

    # 1. Run the Builder Agent
    print("\n--- Initializing Architect Agent ---")
    build_city(target_dir, output_file)

    # 2. Start the Server
    print("\n--- Booting Web Server ---")
    start_server(args.port, public_dir)

if __name__ == "__main__":
    main()