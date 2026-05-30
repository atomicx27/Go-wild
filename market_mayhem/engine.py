import random
import time
from typing import Dict, List, Optional
import threading

class Stock:
    def __init__(self, ticker: str, initial_price: float, volatility: float):
        self.ticker = ticker
        self.price = initial_price
        self.history: List[float] = [initial_price]
        self.volatility = volatility

    def update_price(self, sentiment_shift: float = 0.0):
        # Random walk with drift based on sentiment
        change_pct = random.gauss(sentiment_shift, self.volatility)
        self.price = max(0.01, self.price * (1 + change_pct))
        self.history.append(self.price)
        if len(self.history) > 100:
            self.history.pop(0)

class MarketEngine:
    def __init__(self):
        self.stocks: Dict[str, Stock] = {
            "NEXUS": Stock("NEXUS", 150.0, 0.02),
            "VOID": Stock("VOID", 25.0, 0.05),
            "ECHO": Stock("ECHO", 300.0, 0.015),
            "PULSE": Stock("PULSE", 10.0, 0.1),
        }
        self.news_ticker: List[str] = ["Market opens. Volatility expected."]
        self.running = False
        self.market_sentiment_shift = 0.0

    def add_news(self, news: str):
        self.news_ticker.append(news)
        if len(self.news_ticker) > 5:
            self.news_ticker.pop(0)

    def execute_trade(self, agent_name: str, ticker: str, action: str, quantity: int, agent_portfolio: Dict) -> bool:
        if ticker not in self.stocks:
            return False

        stock = self.stocks[ticker]
        total_cost = stock.price * quantity

        if action == "BUY":
            if agent_portfolio["cash"] >= total_cost:
                agent_portfolio["cash"] -= total_cost
                agent_portfolio["holdings"][ticker] = agent_portfolio["holdings"].get(ticker, 0) + quantity
                # Slight upward pressure
                stock.update_price(0.001 * quantity)
                return True
        elif action == "SELL":
            if agent_portfolio["holdings"].get(ticker, 0) >= quantity:
                agent_portfolio["cash"] += total_cost
                agent_portfolio["holdings"][ticker] -= quantity
                # Slight downward pressure
                stock.update_price(-0.001 * quantity)
                return True
        return False

    def step(self):
        for stock in self.stocks.values():
            stock.update_price(self.market_sentiment_shift)

        # Mean reversion for sentiment
        self.market_sentiment_shift *= 0.9

    def start(self, interval: float = 2.0):
        self.running = True
        def run_loop():
            while self.running:
                self.step()
                time.sleep(interval)

        threading.Thread(target=run_loop, daemon=True).start()

    def stop(self):
        self.running = False
