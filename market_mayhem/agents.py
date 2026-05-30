import json
import requests
import re
from typing import Dict, List, Optional
import time

OLLAMA_API_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3"

def query_ollama(messages: List[Dict], model: str = DEFAULT_MODEL) -> str:
    """Send a query to Ollama and return the response text."""
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={"model": model, "messages": messages, "stream": False},
            timeout=30
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ollama: {e}"

def extract_json(text: str) -> Optional[Dict]:
    """Extract and parse JSON from a string."""
    try:
        # Find JSON block
        json_match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Fallback: try to find anything that looks like a JSON object
            json_match = re.search(r'(\{.*\})', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                return None
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None

class NewsAnchor:
    def __init__(self):
        self.system_prompt = (
            "You are a chaotic, sensationalist financial news anchor in a cyberpunk dystopia. "
            "Write a short, punchy, 1-2 sentence breaking news headline about the market or a specific stock (NEXUS, VOID, ECHO, PULSE). "
            "It can be good news, bad news, or completely bizarre. "
            "Format your output as a simple string, no quotes, no extra text."
        )

    def generate_news(self, current_market_state: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Current market state: {current_market_state}\nGive me breaking news!"}
        ]
        return query_ollama(messages).strip()

class TraderAgent:
    def __init__(self, name: str, persona: str, initial_cash: float):
        self.name = name
        self.persona = persona
        self.portfolio = {"cash": initial_cash, "holdings": {}}
        self.last_thought = "Waiting for the market to open..."

        self.system_prompt = f"""
        You are an autonomous stock trader. Your name is {self.name}.
        Your persona: {self.persona}.

        You will be provided with the current stock prices, your portfolio, and recent news.
        You must decide whether to BUY, SELL, or HOLD a specific stock.

        You MUST respond ONLY with a valid JSON object in the following format:
        ```json
        {{
            "thought": "Your internal monologue and reasoning based on your persona.",
            "action": "BUY" | "SELL" | "HOLD",
            "ticker": "NEXUS" | "VOID" | "ECHO" | "PULSE" | "NONE",
            "quantity": <integer>
        }}
        ```
        If you HOLD, set ticker to "NONE" and quantity to 0.
        Only BUY if you have enough cash. Only SELL if you have enough holdings.
        """

    def decide_action(self, market_data: str) -> Optional[Dict]:
        user_prompt = f"Market Data:\n{market_data}\n\nWhat is your next move?"
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response_text = query_ollama(messages)
        parsed_action = extract_json(response_text)

        if parsed_action and "thought" in parsed_action:
            self.last_thought = parsed_action["thought"]

        return parsed_action

    def get_net_worth(self, current_prices: Dict[str, float]) -> float:
        nw = self.portfolio["cash"]
        for ticker, qty in self.portfolio["holdings"].items():
            if ticker in current_prices:
                nw += qty * current_prices[ticker]
        return nw
