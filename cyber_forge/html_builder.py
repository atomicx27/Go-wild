import json
from pathlib import Path
import html

def build_armory_html(armory_dir: Path):
    """
    Scans the armory directory for forged tools and builds a modern,
    cyberpunk-themed HTML dashboard to view them.
    """
    tools = []

    # Each tool in armory is saved as a JSON metadata file + .py + test_.py
    for meta_file in armory_dir.glob("*.json"):
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            code_file = armory_dir / meta.get("code_file", "")
            test_file = armory_dir / meta.get("test_file", "")

            code_content = ""
            test_content = ""

            if code_file.exists():
                code_content = code_file.read_text(encoding='utf-8')
            if test_file.exists():
                test_content = test_file.read_text(encoding='utf-8')

            tools.append({
                "name": meta.get("name", meta_file.stem),
                "description": meta.get("description", ""),
                "attempts": meta.get("attempts", 0),
                "code": code_content,
                "test": test_content
            })
        except Exception as e:
            print(f"Error loading {meta_file}: {e}")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyber Forge | Armory</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
    <style>
        body {{
            background-color: #050505;
            color: #00ffcc;
            font-family: 'Courier New', Courier, monospace;
        }}
        .neon-text {{
            text-shadow: 0 0 5px #00ffcc, 0 0 10px #00ffcc, 0 0 20px #00ffcc;
        }}
        .neon-border {{
            border: 1px solid #00ffcc;
            box-shadow: 0 0 10px #00ffcc, inset 0 0 10px #00ffcc;
        }}
        .card:hover {{
            box-shadow: 0 0 20px #ff00ff, inset 0 0 10px #ff00ff;
            border-color: #ff00ff;
            transition: all 0.3s ease;
        }}
        .glass {{
            background: rgba(10, 10, 10, 0.8);
            backdrop-filter: blur(10px);
        }}
        pre[class*="language-"] {{
            background: #111;
            border-left: 4px solid #ff00ff;
            margin-top: 1rem;
        }}
        code[class*="language-"] {{
            color: #00ffcc;
        }}
    </style>
</head>
<body class="min-h-screen bg-[url('https://www.transparenttextures.com/patterns/cubes.png')]">
    <div class="container mx-auto px-4 py-8 relative z-10">
        <header class="text-center mb-12">
            <h1 class="text-6xl font-bold mb-4 neon-text tracking-widest uppercase">Cyber Forge</h1>
            <p class="text-xl text-purple-400">Autonomous Self-Healing Code Factory</p>
            <div class="mt-4 h-1 w-64 mx-auto bg-gradient-to-r from-transparent via-cyan-400 to-transparent"></div>
        </header>

        <main>
            <div class="flex justify-between items-center mb-8 border-b border-cyan-900 pb-2">
                <h2 class="text-3xl font-semibold">The Armory</h2>
                <span class="bg-cyan-900 text-cyan-200 px-3 py-1 rounded text-sm font-bold shadow-[0_0_10px_#00ffcc]">
                    Tools Forged: {len(tools)}
                </span>
            </div>

            <div class="grid grid-cols-1 gap-8">
"""

    if not tools:
        html_content += """
                <div class="text-center py-16 neon-border rounded-lg glass">
                    <p class="text-2xl text-gray-500 mb-4">Armory is empty.</p>
                    <p class="text-gray-600">Drop an idea file into the <code class="text-cyan-400 bg-gray-900 px-2 py-1 rounded">inbox/</code> to begin forging.</p>
                </div>
"""
    else:
        for tool in tools:
            escaped_code = html.escape(tool["code"])
            escaped_test = html.escape(tool["test"])

            html_content += f"""
                <div class="card neon-border rounded-lg p-6 glass transition-all">
                    <div class="flex justify-between items-start mb-4">
                        <h3 class="text-2xl font-bold text-fuchsia-400 uppercase">{html.escape(tool["name"])}</h3>
                        <span class="bg-fuchsia-900 text-fuchsia-200 text-xs px-2 py-1 rounded border border-fuchsia-400">
                            Forged in {tool["attempts"]} attempts
                        </span>
                    </div>
                    <p class="text-gray-300 mb-6 italic border-l-2 border-cyan-600 pl-4 py-1">
                        {html.escape(tool["description"])}
                    </p>

                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div>
                            <h4 class="text-cyan-300 font-semibold mb-2 flex items-center">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg>
                                Source Code
                            </h4>
                            <pre><code class="language-python">{escaped_code}</code></pre>
                        </div>
                        <div>
                            <h4 class="text-fuchsia-300 font-semibold mb-2 flex items-center">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                Test Suite
                            </h4>
                            <pre><code class="language-python">{escaped_test}</code></pre>
                        </div>
                    </div>
                </div>
"""

    html_content += """
            </div>
        </main>

        <footer class="mt-16 text-center text-gray-600 text-sm border-t border-gray-800 pt-4">
            <p>Cyber Forge &copy; Artificial Intelligence System</p>
            <p class="mt-1 text-xs">Self-healing agentic loop initialized.</p>
        </footer>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
</body>
</html>
"""

    index_path = armory_dir / "index.html"
    index_path.write_text(html_content, encoding='utf-8')
    print(f"Dashboard updated at {index_path}")
    return index_path
