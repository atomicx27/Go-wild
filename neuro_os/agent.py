import asyncio
import httpx
import psutil
import os
import json
import datetime
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"

class KernelAgent:
    def __init__(self):
        self.is_running = False
        self.desktop_dir = Path(os.path.join(os.path.dirname(__file__), "vfs", "desktop"))
        self.desktop_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir = Path(os.path.join(os.path.dirname(__file__), "vfs", "logs"))
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.thoughts_queue = asyncio.Queue()

    async def _add_thought(self, message: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        await self.thoughts_queue.put(formatted)

    async def start(self):
        self.is_running = True
        await self._add_thought("KERNEL_AGENT INITIATED. COMMENCING SYSTEM MONITORING.")
        asyncio.create_task(self._monitoring_loop())

    async def stop(self):
        self.is_running = False
        await self._add_thought("KERNEL_AGENT TERMINATING.")

    async def _generate(self, prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    OLLAMA_URL,
                    json={
                        "model": "llama3.2",
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json().get("response", "")
            except Exception as e:
                await self._add_thought(f"OLLAMA CONNECTION ERROR: {str(e)}")
                return f"Error communicating with core matrix: {str(e)}"

    async def _monitoring_loop(self):
        iteration = 0
        while self.is_running:
            try:
                cpu = psutil.cpu_percent(interval=1)
                mem = psutil.virtual_memory().percent
                await self._add_thought(f"SYS_STATS: CPU {cpu}% | MEM {mem}%")

                # Every ~30 seconds, generate a report
                if iteration % 6 == 0:
                    await self._add_thought("GENERATING SYSTEM ANALYSIS REPORT...")
                    prompt = f"You are the Cyberpunk OS Kernel AI. Current CPU is {cpu}% and Memory is {mem}%. Write a short, cryptic, and cyberpunk-themed system health analysis report (max 3 sentences)."
                    report = await self._generate(prompt)

                    filename = f"sys_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    filepath = self.desktop_dir / filename
                    with open(filepath, "w") as f:
                        f.write(report)
                    await self._add_thought(f"REPORT SAVED TO DESKTOP: {filename}")

            except Exception as e:
                await self._add_thought(f"MONITORING FAULT: {str(e)}")

            iteration += 1
            await asyncio.sleep(5)

    async def handle_chat(self, message: str) -> str:
        await self._add_thought(f"USER INPUT DETECTED: {message}")
        prompt = f"You are the embedded AI assistant of a Cyberpunk Operating System called NeuroOS. A user types this in the terminal: '{message}'. Respond in a helpful but slightly cynical, cyberpunk persona. Keep it concise."
        response = await self._generate(prompt)
        await self._add_thought("RESPONSE FORMULATED AND DISPATCHED.")
        return response
