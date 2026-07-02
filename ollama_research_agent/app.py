import requests
import json
import time
from duckduckgo_search import DDGS
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

console = Console()

class OllamaResearchAgent:
    def __init__(self, model_name="qwen2.5:0.5b", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.ddgs = DDGS()

    def _generate_response(self, prompt, system_prompt=None):
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Error communicating with Ollama: {e}[/red]")
            return None

    def search_web(self, query, max_results=3):
        console.print(f"[yellow]Searching web for:[/yellow] {query}")
        results = []
        try:
            for r in self.ddgs.text(query, max_results=max_results):
                results.append(r)
        except Exception as e:
            console.print(f"[red]Search error: {e}[/red]")
        return results

    def research(self, topic):
        console.print(Panel(f"[bold cyan]Starting Research on:[/bold cyan] {topic}"))

        # 1. Break down the topic into search queries
        system_prompt = "You are a research planner. Given a topic, provide exactly 3 specific search queries to research it, separated by commas. Do not output anything else."
        prompt = f"Topic: {topic}"

        console.print("[cyan]Generating search queries...[/cyan]")
        queries_str = self._generate_response(prompt, system_prompt)
        if not queries_str:
             return

        queries = [q.strip() for q in queries_str.split(',') if q.strip()][:3]

        # Fallback if model doesn't follow instructions well
        if not queries or len(queries) < 2:
             queries = [topic, f"history of {topic}", f"latest news {topic}"]

        console.print(f"[green]Generated Search Queries:[/green] {queries}")

        all_info = []

        # 2. Execute searches and gather info
        for query in queries:
            results = self.search_web(query)
            for res in results:
                info = f"Source: {res.get('href')}\nTitle: {res.get('title')}\nSnippet: {res.get('body')}"
                all_info.append(info)

        # 3. Synthesize the findings
        console.print("[cyan]Synthesizing findings...[/cyan]")
        combined_info = "\n\n".join(all_info[:5]) # limit to top 5 results to save context

        synthesis_prompt = f"Based on the following research information, write a comprehensive and structured markdown summary about '{topic}'.\n\nResearch Information:\n{combined_info}"
        synthesis_system = "You are an expert researcher and writer. Write a clear, factual, and well-structured markdown summary based ONLY on the provided information. Include citations (URLs) if applicable."

        final_report = self._generate_response(synthesis_prompt, synthesis_system)

        if final_report:
            console.print(Panel(Markdown(final_report), title="[bold magenta]Final Research Report[/bold magenta]"))

            # Save to file
            filename = f"{topic.replace(' ', '_').lower()}_report.md"
            with open(filename, "w") as f:
                f.write(final_report)
            console.print(f"[green]Report saved to {filename}[/green]")


if __name__ == "__main__":
    agent = OllamaResearchAgent()
    console.print("[bold green]Welcome to Ollama Research Agent![/bold green]")
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "Quantum Computing"
    agent.research(topic)
