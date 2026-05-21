import os
import time
import shutil
import json
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from pathlib import Path

# Cyber Scout Configuration
BASE_DIR = Path(__file__).parent
INBOX_DIR = BASE_DIR / "inbox"
OUTBOX_DIR = BASE_DIR / "outbox"
ARCHIVE_DIR = BASE_DIR / "archive"

def ensure_directories():
    """Ensure that the necessary directories exist."""
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

def process_query(filepath: Path):
    """Reads a query from a file and returns its content."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"[!] Error reading {filepath}: {e}")
        return None

def perform_search(query: str, max_results: int = 3):
    """Searches DuckDuckGo and returns a list of URLs."""
    print(f"[*] Searching for: '{query}'")
    urls = []
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            for r in results:
                urls.append(r.get('href'))
    except Exception as e:
        print(f"[!] Search error: {e}")
    return urls

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

def synthesize_with_ollama(query: str, context: str):
    """Sends the query and context to Ollama for synthesis."""
    print("[*] Synthesizing report with Ollama...")
    prompt = f"""
    You are CyberScout, an advanced AI research agent.
    Your user asked the following query: {query}

    Based on your web search, you found the following information:
    ---
    {context}
    ---

    Synthesize this information into a cohesive, highly informative, and well-structured response.
    Format your response purely in Markdown. Do not include any generic introductory or concluding remarks.
    """

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response generated.")
    except Exception as e:
        print(f"[!] Error communicating with Ollama: {e}")
        print("[*] Falling back to mock synthesis...")
        fallback_markdown = f"""
## ⚠️ AI Core Offline ⚠️
*System unable to establish connection with local Ollama instance (`{OLLAMA_URL}`).*
*Bypassing synthesis protocol and displaying raw intercepted datastreams...*

### Raw Datastreams:
{context}
"""
        return fallback_markdown

def generate_html_report(query: str, markdown_content: str):
    """Wraps the markdown content in a Cyberpunk-styled HTML template."""
    import markdown
    html_content = markdown.markdown(markdown_content, extensions=['fenced_code', 'tables'])

    template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CyberScout Dossier: {query}</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
            body {{
                font-family: 'Share Tech Mono', monospace;
                background-color: #050505;
                color: #00ff41;
                background-image:
                    linear-gradient(rgba(0, 255, 65, 0.05) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0, 255, 65, 0.05) 1px, transparent 1px);
                background-size: 20px 20px;
            }}
            .scanline {{
                width: 100%;
                height: 100px;
                z-index: 9999;
                position: fixed;
                pointer-events: none;
                background: linear-gradient(0deg, rgba(0,0,0,0) 0%, rgba(0,255,65,0.1) 50%, rgba(0,0,0,0) 100%);
                animation: scanline 6s linear infinite;
            }}
            @keyframes scanline {{
                0% {{ top: -100px; }}
                100% {{ top: 100%; }}
            }}
            .glitch-hover:hover {{
                animation: glitch-skew 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) both infinite;
                color: #fff;
                text-shadow: 2px 2px #ff003c, -2px -2px #00e6f6;
            }}
            .markdown-body h1 {{ font-size: 2.5rem; color: #ff003c; margin-bottom: 1rem; border-bottom: 1px solid #ff003c; }}
            .markdown-body h2 {{ font-size: 2rem; color: #00e6f6; margin-top: 1.5rem; margin-bottom: 1rem; border-bottom: 1px dashed #00e6f6; }}
            .markdown-body h3 {{ font-size: 1.5rem; color: #fce205; margin-top: 1.2rem; margin-bottom: 0.8rem; }}
            .markdown-body p {{ margin-bottom: 1rem; line-height: 1.6; }}
            .markdown-body a {{ color: #00e6f6; text-decoration: underline; }}
            .markdown-body ul {{ list-style-type: square; padding-left: 2rem; margin-bottom: 1rem; }}
            .markdown-body code {{ background-color: #1a1a1a; padding: 0.2rem 0.4rem; border-radius: 0.2rem; color: #fce205; }}
            .markdown-body pre {{ background-color: #1a1a1a; padding: 1rem; border-left: 4px solid #ff003c; overflow-x: auto; margin-bottom: 1rem; }}

            /* Glowing borders */
            .neon-border {{
                border: 1px solid #00ff41;
                box-shadow: 0 0 10px rgba(0, 255, 65, 0.5), inset 0 0 10px rgba(0, 255, 65, 0.2);
            }}
        </style>
    </head>
    <body class="min-h-screen p-8 relative">
        <div class="scanline"></div>

        <header class="max-w-4xl mx-auto mb-8 border-b-2 border-[#00ff41] pb-4 flex justify-between items-end">
            <div>
                <h1 class="text-4xl font-bold glitch-hover uppercase tracking-widest">CYBERSCOUT // TERMINAL</h1>
                <p class="text-sm text-gray-400 mt-2">CLASSIFIED DOSSIER - LEVEL 4 CLEARANCE</p>
            </div>
            <div class="text-right">
                <p class="text-[#fce205]">QUERY REF: <span class="uppercase">{query[:20]}...</span></p>
                <p class="text-xs text-gray-500">SYSTEM: SECURE // CONNECTION: STABLE</p>
            </div>
        </header>

        <main class="max-w-4xl mx-auto bg-black bg-opacity-70 p-8 neon-border relative overflow-hidden">
            <!-- Decorative corners -->
            <div class="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-[#ff003c]"></div>
            <div class="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-[#ff003c]"></div>
            <div class="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-[#ff003c]"></div>
            <div class="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-[#ff003c]"></div>

            <div class="markdown-body">
                {html_content}
            </div>
        </main>

        <footer class="max-w-4xl mx-auto mt-8 text-center text-xs text-gray-600">
            &copy; CYBERSCOUT AUTOMATED INTELLIGENCE GATHERING PROTOCOL
        </footer>
    </body>
    </html>
    """
    return template

def scrape_url(url: str):
    """Fetches and extracts text from a URL."""
    print(f"[*] Scraping: {url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text(separator=' ', strip=True)
        # Limit the text length to avoid context window overflow
        return text[:4000]
    except Exception as e:
        print(f"[!] Error scraping {url}: {e}")
        return ""

def archive_file(filepath: Path):
    """Moves a processed file to the archive directory."""
    try:
        dest = ARCHIVE_DIR / filepath.name
        shutil.move(str(filepath), str(dest))
        print(f"[*] Archived {filepath.name}")
    except Exception as e:
        print(f"[!] Error archiving {filepath}: {e}")

def save_report(query_name: str, content: str):
    """Saves the generated report to the outbox."""
    report_name = f"{query_name}_report.html"
    report_path = OUTBOX_DIR / report_name
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[+] Saved report to {report_name}")
    except Exception as e:
        print(f"[!] Error saving report: {e}")

def main():
    print("[*] Cyber Scout Agent initialized.")
    ensure_directories()

    print("[*] Watching inbox for new queries...")
    try:
        while True:
            for file in INBOX_DIR.glob("*.txt"):
                print(f"\n[*] Found new query: {file.name}")
                query = process_query(file)
                if not query:
                    continue

                print(f"[*] Processing query: '{query}'")

                urls = perform_search(query)
                scraped_data = []
                for url in urls:
                    content = scrape_url(url)
                    if content:
                        scraped_data.append(f"Source: {url}\nContent: {content}...\n")

                context = "\n\n".join(scraped_data)

                if not context:
                    context = "No relevant information found on the web."

                markdown_result = synthesize_with_ollama(query, context)
                final_html = generate_html_report(query, markdown_result)

                save_report(file.stem, final_html)
                archive_file(file)

            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[*] Cyber Scout shutting down.")

if __name__ == "__main__":
    main()
