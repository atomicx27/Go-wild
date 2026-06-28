import sys
import time
import random
import requests
import argparse
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.layout import Layout
from rich import print as rprint

console = Console()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:0.5b"

ASCII_ARTS = [
    r"""
    ___  _   _
   / _ \| | | |
  | | | | | | |
  | |_| | |_| |
   \___/ \___/
    """,
    r"""
     |\__/,|   (`\
   _.|o o  |_   ) )
  -(((---(((--------
    """,
    r"""
  /$$$$$$  /$$     /$$ /$$$$$$$  /$$$$$$$$ /$$$$$$$
 /$$__  $$|  $$   /$$/| $$__  $$| $$_____/| $$__  $$
| $$  \__/ \  $$ /$$/ | $$  \ $$| $$      | $$  \ $$
| $$        \  $$$$/  | $$$$$$$/| $$$$$   | $$$$$$$/
| $$         \  $$/   | $$__  $$| $$__/   | $$__  $$
| $$    $$    | $$    | $$  \ $$| $$      | $$  \ $$
|  $$$$$$/    | $$    | $$$$$$$/| $$$$$$$$| $$  | $$
 \______/     |__/    |_______/ |________/|__/  |__/
    """,
    r"""
   .     .       .  .   . .   .   . .    +  .
  .     .  :     .    .. :. .___---------___.
       .  .   .    .  :.:. _".^ .^ ^.  '.. :"-_. .
    .  :       .  .  .:../:            . .^  :.:\.
        .   . :: +. :.:/: .   .    .        . . .:\
 .  :    .     . _ :::/:               .  ^ .  . .:\
  .. . .   . - : :.:./.                        .  .:\
  .      .     . :..|:                    .  .  ^. .:|
    .       . : : ..||        .                . . !:|
  .     . . . ::. ::\(                           . :)/
 .   .     : . : .:.|. ######              .#######::|
  :.. .  :-  : .:  ::|.#######           ..########:|
 .  .  .  ..  .  .. :\ ########          :######## :/
  .        .+ :: : -.:\ ########       . ########.:/
    .  .+   . . . . :.:\. #######       #######..:/
      :: . . . . ::.:..:.\           .   .   ..:/
   .   .   .  .. :  -::::.\.       | |     . .:/
      .  :  .  .  .-:.":.::.\             ..:/
 .      -.   . . . .: .:::.:.\.           .:/
.   .   .  :      : ....::_:..:\   ___.  :/
   .   .  .   .:. .. .  .: :.:.:\       :/
     +   .   .   : . ::. :.:. .:.|\  .:/|
     .         +   .  .  ...:: ..|  --.:|
.      . . .   .  .  . ... :..:.."(  ..)"
 .   .       .      :  .   .: ::/  .  .::\
    """
]

COLORS = [
    "red", "green", "yellow", "blue", "magenta", "cyan",
    "bright_red", "bright_green", "bright_yellow",
    "bright_blue", "bright_magenta", "bright_cyan"
]

def generate_rap(topic):
    prompt = f"Write a short, wild, rhyming cyber-rap or tech-poem about {topic}. Make it high-energy, full of slang, and completely unhinged. No introduction or explanation, just the rap."

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "Yo, the mic is broken, error 404, the bot has spoken.")
    except Exception as e:
        return f"System failure, beep boop. The DJ is down: {e}"

def drop_the_beat(rap_text):
    lines = rap_text.strip().split("\n")

    console.print(Panel("[bold bright_green]DJ TERMINAL IS IN THE HOUSE[/bold bright_green]", expand=False))
    time.sleep(1)

    for line in lines:
        if not line.strip():
            continue

        color = random.choice(COLORS)
        style = random.choice(["bold", "italic", "bold italic", ""])

        # Inject random ASCII art occasionally
        if random.random() < 0.15:
            art = random.choice(ASCII_ARTS)
            art_color = random.choice(COLORS)
            console.print(Text(art, style=f"bold {art_color}"))
            time.sleep(0.5)

        text = Text()
        text.append("🔥 ", style="bold red")

        # Typewriter effect
        for char in line:
            text.append(char, style=f"{style} {color}".strip())
            console.print(text, end="\r")
            time.sleep(random.uniform(0.01, 0.05))

        # Print final line with a newline to move to the next line
        console.print(text)
        time.sleep(random.uniform(0.3, 0.8))

    console.print(Panel("[bold bright_red]MIC DROP.[/bold bright_red]", expand=False))

def main():
    parser = argparse.ArgumentParser(description="Terminal DJ: An unhinged AI hype-man")
    parser.add_argument("topic", nargs="?", default="hacking the mainframe with a toaster", help="What should the DJ rap about?")
    args = parser.parse_args()

    with console.status("[bold magenta]DJ is mixing the tracks (asking Ollama)...[/bold magenta]", spinner="bouncingBar"):
        rap = generate_rap(args.topic)

    console.clear()
    drop_the_beat(rap)

if __name__ == "__main__":
    main()
