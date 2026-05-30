import time
import threading
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from engine import MarketEngine
from agents import TraderAgent, NewsAnchor

def make_layout() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="news", size=5)
    )
    layout["main"].split_row(
        Layout(name="market", ratio=1),
        Layout(name="agents", ratio=2)
    )
    return layout

def update_ui(layout: Layout, engine: MarketEngine, agents: list[TraderAgent]):
    # Header
    layout["header"].update(Panel(Text("MARKET MAYHEM: Cyberpunk Terminal", justify="center", style="bold cyan"), style="cyan"))

    # Market Table
    market_table = Table(box=box.MINIMAL_DOUBLE_HEAD, style="cyan")
    market_table.add_column("Ticker", style="magenta")
    market_table.add_column("Price", justify="right", style="green")

    for ticker, stock in engine.stocks.items():
        price_color = "green"
        if len(stock.history) >= 2 and stock.price < stock.history[-2]:
            price_color = "red"

        market_table.add_row(ticker, f"[{price_color}]${stock.price:.2f}[/{price_color}]")

    layout["market"].update(Panel(market_table, title="[yellow]Live Market[/yellow]", border_style="cyan"))

    # Agents Table
    agents_table = Table(box=box.MINIMAL_DOUBLE_HEAD, style="cyan")
    agents_table.add_column("Agent", style="blue")
    agents_table.add_column("Net Worth", justify="right", style="green")
    agents_table.add_column("Current Holdings", style="yellow")
    agents_table.add_column("Last Thought", style="italic white")

    current_prices = {t: s.price for t, s in engine.stocks.items()}

    for agent in agents:
        nw = agent.get_net_worth(current_prices)
        holdings_str = ", ".join([f"{k}:{v}" for k, v in agent.portfolio["holdings"].items() if v > 0])
        if not holdings_str:
            holdings_str = "None"

        thought_trunc = agent.last_thought[:60] + "..." if len(agent.last_thought) > 60 else agent.last_thought
        agents_table.add_row(agent.name, f"${nw:.2f}", holdings_str, thought_trunc)

    layout["agents"].update(Panel(agents_table, title="[yellow]Traders[/yellow]", border_style="cyan"))

    # News Ticker
    news_text = "\n".join(engine.news_ticker[-3:])
    layout["news"].update(Panel(Text(news_text, style="bold red"), title="[yellow]Breaking News[/yellow]", border_style="red"))


def run_simulation(engine: MarketEngine, agents: list[TraderAgent], anchor: NewsAnchor):
    loop_count = 0
    while True:
        try:
            # Generate News occasionally
            if loop_count % 10 == 0:
                current_market_state = ", ".join([f"{t}: ${s.price:.2f}" for t, s in engine.stocks.items()])
                news = anchor.generate_news(current_market_state)
                engine.add_news(news)

                # Affect sentiment
                if "good" in news.lower() or "soars" in news.lower():
                    engine.market_sentiment_shift += 0.05
                elif "bad" in news.lower() or "plummets" in news.lower() or "crash" in news.lower():
                    engine.market_sentiment_shift -= 0.05

            # Agents trade
            for agent in agents:
                current_market_state = f"Prices: {', '.join([f'{t}: ${s.price:.2f}' for t, s in engine.stocks.items()])}. News: {engine.news_ticker[-1]}"
                action_data = agent.decide_action(current_market_state)
                if action_data:
                    action = action_data.get("action")
                    ticker = action_data.get("ticker")
                    qty = action_data.get("quantity", 0)
                    if action in ["BUY", "SELL"] and ticker != "NONE" and qty > 0:
                         success = engine.execute_trade(agent.name, ticker, action, qty, agent.portfolio)
                         if success:
                             engine.add_news(f"TRACE: {agent.name} {action} {qty} {ticker}")

            loop_count += 1
            time.sleep(5)
        except Exception as e:
            engine.add_news(f"ERROR: {e}")
            time.sleep(5)

def main():
    engine = MarketEngine()
    anchor = NewsAnchor()
    agents = [
        TraderAgent("DiamondHands Ape", "You buy everything recklessly and never sell, hoping for 'moon'. Extremely optimistic.", 5000.0),
        TraderAgent("The Suit", "You are a cold, calculating Wall Street veteran. You prefer stable stocks and panic sell when volatility hits.", 5000.0),
        TraderAgent("Chaos Bot", "You make random, illogical trades just to cause market instability. You love volatile stocks.", 5000.0)
    ]

    engine.start(interval=1.0) # Engine ticks fast for random walk

    sim_thread = threading.Thread(target=run_simulation, args=(engine, agents, anchor), daemon=True)
    sim_thread.start()

    layout = make_layout()
    try:
        with Live(layout, refresh_per_second=2, screen=True):
            while True:
                update_ui(layout, engine, agents)
                time.sleep(0.5)
    except KeyboardInterrupt:
        engine.stop()
        print("Market simulation terminated.")

if __name__ == "__main__":
    main()
