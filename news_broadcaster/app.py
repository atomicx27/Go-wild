import asyncio
import feedparser
import requests
from bs4 import BeautifulSoup
import edge_tts

def get_hacker_news():
    print("Fetching Hacker News RSS...")
    feed = feedparser.parse("https://hnrss.org/frontpage")
    entries = feed.entries[:5]
    news_items = []
    for entry in entries:
        title = entry.title
        summary = BeautifulSoup(entry.summary, "html.parser").get_text()
        news_items.append(f"Title: {title}\nSummary: {summary}")
    return "\n\n".join(news_items)

def generate_script(news_content):
    print("Generating script with Ollama...")
    prompt = f"""You are a professional radio news broadcaster. Here are the top tech stories of the day:

{news_content}

Write a short, engaging radio news script (under 150 words) summarizing these stories for your listeners. Start with an exciting intro, mention a couple of the top stories, and end with a sign-off. ONLY output the script text, with no extra commentary or formatting. DO NOT output markdown. Do not include sound effect cues like *ding* or [music]."""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return "Welcome to the news. We had some technical difficulties fetching the stories today. Stay tuned for more updates."

async def generate_audio(script_text):
    print("Generating audio with edge-tts...")
    voice = "en-US-ChristopherNeural"
    output_file = "broadcast.mp3"
    communicate = edge_tts.Communicate(script_text, voice)
    await communicate.save(output_file)
    print(f"Audio saved to {output_file}")

async def main():
    news_content = get_hacker_news()
    script = generate_script(news_content)
    print("\n--- Generated Script ---")
    print(script)
    print("------------------------\n")
    await generate_audio(script)

if __name__ == "__main__":
    asyncio.run(main())
