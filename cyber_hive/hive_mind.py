import asyncio
import os
import httpx
from datetime import datetime

class HiveMind:
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = ollama_url
        self.base_dir = os.path.dirname(__file__)
        self.inbox_dir = os.path.join(self.base_dir, "inbox")
        self.outbox_dir = os.path.join(self.base_dir, "outbox")
        self.rejected_dir = os.path.join(self.base_dir, "rejected")

        os.makedirs(self.inbox_dir, exist_ok=True)
        os.makedirs(self.outbox_dir, exist_ok=True)
        os.makedirs(self.rejected_dir, exist_ok=True)

        self.log_queue = asyncio.Queue()
        self.running = False

    async def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        await self.log_queue.put(log_msg)
        print(log_msg)

    async def process_with_ollama(self, prompt: str) -> str:
        await self.log(f"INITIATING HIVE MIND LINK... Sending query to Ollama.")
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                payload = {
                    "model": "llama3",
                    "messages": [
                        {"role": "system", "content": "You are the Cyber Hive AI, an autonomous intelligence processing unstructured data requests. Provide clean, well-formatted, and accurate output."},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False
                }
                response = await client.post(f"{self.ollama_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                await self.log("HIVE MIND LINK SUCCESS: Response received.")
                return data["message"]["content"]
        except Exception as e:
            await self.log(f"CRITICAL ERROR IN LINK: {str(e)}")
            raise

    async def watch_inbox(self):
        self.running = True
        await self.log("CYBER HIVE ACTIVATED. Monitoring inbox...")
        while self.running:
            try:
                for filename in os.listdir(self.inbox_dir):
                    if filename.endswith(".txt"):
                        filepath = os.path.join(self.inbox_dir, filename)
                        await self.log(f"NEW DATA DETECTED: {filename}")

                        try:
                            with open(filepath, "r") as f:
                                prompt = f.read()

                            response = await self.process_with_ollama(prompt)

                            outbox_path = os.path.join(self.outbox_dir, f"processed_{filename}")
                            with open(outbox_path, "w") as f:
                                f.write(response)

                            await self.log(f"PROCESSING COMPLETE. Output saved to {outbox_path}")
                            os.remove(filepath)

                        except Exception as e:
                            await self.log(f"PROCESSING FAILED for {filename}. Moving to rejected.")
                            rejected_path = os.path.join(self.rejected_dir, filename)
                            os.rename(filepath, rejected_path)

            except Exception as e:
                await self.log(f"SYSTEM ERROR in watcher loop: {str(e)}")

            await asyncio.sleep(3)

        await self.log("CYBER HIVE SHUTDOWN.")
