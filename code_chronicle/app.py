import os
import subprocess
import json
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import asyncio

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Code Chronicle")
# No static files yet

def get_git_log(max_commits: int = 10) -> List[Dict[str, str]]:
    """Retrieves the recent git log."""
    try:
        # Get hash, author date, message
        cmd = ["git", "log", f"-n {max_commits}", "--pretty=format:%H|%ad|%s", "--date=short"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|', 2)
                if len(parts) == 3:
                    commits.append({
                        "hash": parts[0],
                        "date": parts[1],
                        "message": parts[2]
                    })
        return commits
    except Exception as e:
        logger.error(f"Error getting git log: {e}")
        return []

async def generate_lore(commit_msg: str, commit_hash: str) -> str:
    """Uses Ollama to generate lore for a commit."""
    prompt = f"""
    You are the Chronicler, a wise and dramatic narrator in a fantasy setting.
    A developer has made a change to the realm's magical codebase.

    The commit message is: "{commit_msg}"

    Write a short, 1-2 sentence dramatic and slightly humorous "lore" entry describing this event as if it were a historical action taken by a wizard or hero.
    Use words like 'scrolls', 'runes', 'incantation', 'realm', etc.
    Do not include any preamble, just the lore.
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7}
                },
                timeout=60.0 # Increased timeout
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "The chronical details are lost to time...").strip()
    except Exception as e:
        logger.error(f"Error generating lore for commit {commit_hash}: {e}")
        return "The ancient archives failed to retrieve the lore for this event."


@app.get("/api/chronicle")
async def get_chronicle():
    commits = get_git_log(10)

    # Process concurrently
    tasks = [generate_lore(c['message'], c['hash']) for c in commits]
    lores = await asyncio.gather(*tasks)

    for i, commit in enumerate(commits):
        commit['lore'] = lores[i]

    return JSONResponse(content=commits)

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Chronicle</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

        body {
            background-color: #1a1a1a;
            color: #d4d4d4;
            font-family: 'Press Start 2P', monospace;
            padding: 20px;
            margin: 0;
            line-height: 1.6;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
        }

        h1 {
            color: #ffb86c;
            text-align: center;
            text-shadow: 2px 2px #ff79c6;
            margin-bottom: 40px;
        }

        .timeline {
            position: relative;
            padding-left: 30px;
            border-left: 4px solid #6272a4;
        }

        .commit-card {
            background-color: #282a36;
            border: 2px solid #44475a;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            position: relative;
            box-shadow: 4px 4px 0px #44475a;
            transition: transform 0.2s;
        }

        .commit-card:hover {
            transform: translate(-2px, -2px);
            box-shadow: 6px 6px 0px #ff79c6;
            border-color: #ff79c6;
        }

        .commit-card::before {
            content: '';
            position: absolute;
            left: -41px;
            top: 20px;
            width: 16px;
            height: 16px;
            background-color: #8be9fd;
            border: 4px solid #282a36;
            border-radius: 50%;
            z-index: 1;
        }

        .hash {
            color: #8be9fd;
            font-size: 0.7em;
            margin-bottom: 10px;
        }

        .date {
            color: #f1fa8c;
            font-size: 0.7em;
            float: right;
        }

        .message {
            color: #50fa7b;
            margin-bottom: 15px;
            font-size: 0.8em;
        }

        .lore {
            color: #bd93f9;
            font-style: italic;
            border-top: 1px dashed #6272a4;
            padding-top: 15px;
            font-size: 0.8em;
            line-height: 1.8;
        }

        .loading {
            text-align: center;
            color: #ffb86c;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { opacity: 0.5; }
            50% { opacity: 1; }
            100% { opacity: 0.5; }
        }

        .error {
            color: #ff5555;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Code Chronicle</h1>

        <div id="content">
            <div class="loading">Consulting the ancient scrolls... (Loading)</div>
        </div>
    </div>

    <script>
        async function loadChronicle() {
            try {
                const response = await fetch('/api/chronicle');
                if (!response.ok) throw new Error('Failed to fetch chronicle');

                const commits = await response.json();

                const contentDiv = document.getElementById('content');
                if (commits.length === 0) {
                    contentDiv.innerHTML = '<div class="error">No history found in the realm.</div>';
                    return;
                }

                const escapeHTML = str => str.replace(/[&<>'"]/g,
                    tag => ({
                        '&': '&amp;',
                        '<': '&lt;',
                        '>': '&gt;',
                        "'": '&#39;',
                        '"': '&quot;'
                    }[tag] || tag)
                );

                let html = '<div class="timeline">';
                commits.forEach(commit => {
                    const shortHash = commit.hash.substring(0, 7);
                    const safeMessage = escapeHTML(commit.message);
                    const safeLore = escapeHTML(commit.lore);

                    html += `
                        <div class="commit-card">
                            <div class="date">${commit.date}</div>
                            <div class="hash">Commit: [${shortHash}]</div>
                            <div class="message">> ${safeMessage}</div>
                            <div class="lore">"${safeLore}"</div>
                        </div>
                    `;
                });
                html += '</div>';

                contentDiv.innerHTML = html;
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('content').innerHTML = `
                    <div class="error">
                        The magical connection was severed.<br>
                        Please check if the Ollama daemon is running.
                    </div>
                `;
            }
        }

        // Load on start
        loadChronicle();
    </script>
</body>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    # Make sure we're running from correct dir if standalone
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
