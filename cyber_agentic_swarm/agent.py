import json
import httpx
import os
import subprocess
import asyncio

class CyberAgent:
    def __init__(self, websocket=None, model="qwen2.5-coder:1.5b"):
        self.model = model
        self.api_url = "http://localhost:11434/api/generate"
        self.websocket = websocket

    async def _log(self, msg):
        print(msg)
        if self.websocket:
            try:
                await self.websocket.send_text(msg)
            except Exception:
                pass

    async def _generate(self, prompt, system="You are an autonomous AI agent."):
        await self._log(f"⚡ Requesting thoughts from {self.model}...")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.api_url,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "system": system,
                        "stream": False
                    },
                    timeout=120.0
                )
                response.raise_for_status()
                return response.json()["response"]
            except Exception as e:
                await self._log(f"❌ Error communicating with Ollama: {e}")
                return ""

    async def _plan(self, task):
        await self._log("🧠 Analyzing task and formulating execution plan...")
        system_prompt = """You are a strategic planner. Break down the task into concrete, actionable steps.
Output ONLY a JSON list of steps. Each step should be an object with 'action' (e.g., 'write_file', 'run_command', 'think') and 'details' (string).
Do NOT include markdown blocks. Output raw JSON only."""
        prompt = f"Task: {task}\n\nProvide the JSON plan."

        response = await self._generate(prompt, system=system_prompt)
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                 response = response.split("```")[1].strip()
            plan = json.loads(response)
            await self._log(f"✅ Plan formulated: {len(plan)} steps identified.")
            return plan
        except json.JSONDecodeError:
            await self._log(f"⚠️ Failed to parse plan as JSON. Raw output snippet: {response[:100]}...")
            return [{"action": "think", "details": f"Failed to plan automatically. Let's start by trying to accomplish: {task}"}]

    async def execute_step(self, step):
        action = step.get("action", "think")
        details = step.get("details", "")

        await self._log(f"▶️ Executing Action: [{action.upper()}] - {details[:60]}...")

        if action == "write_file":
            system_prompt = "You write files. The user will provide a description of the file. Output ONLY the raw file content, no markdown formatting or explanations."
            content = await self._generate(details, system=system_prompt)
            if content.startswith("```python"):
                 content = content[9:]
            elif content.startswith("```"):
                 content = content[3:]
            if content.endswith("```"):
                 content = content[:-3]

            # Extract filename from details or generate a generic one
            filename = "output.txt"
            if "filename:" in details.lower():
                # simple extraction
                parts = details.lower().split("filename:")
                if len(parts) > 1:
                    filename = parts[1].strip().split(" ")[0].strip(".,\"'")
            elif ".py" in details:
                words = details.split()
                for w in words:
                    if ".py" in w:
                        filename = w.strip(".,\"'")
                        break

            with open(filename, "w") as f:
                f.write(content.strip() + "\n")
            await self._log(f"💾 File written: {filename}")

        elif action == "run_command":
            await self._log(f"⚙️ Running command: {details}")
            try:
                process = await asyncio.create_subprocess_shell(
                    details,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()

                if stdout:
                    await self._log(f"🟢 Output:\n{stdout.decode().strip()[:200]}...")
                if stderr:
                    await self._log(f"🔴 Error:\n{stderr.decode().strip()[:200]}...")
            except Exception as e:
                await self._log(f"🔴 Command failed to execute: {e}")

        elif action == "think":
            thought_prompt = f"Think about this step and provide a brief output: {details}"
            thought_res = await self._generate(thought_prompt, system="You are an AI reasoning engine. Be concise.")
            await self._log(f"🤔 Thought Output: {thought_res}")
        else:
             await self._log(f"⚠️ Unknown action type: {action}")

    async def run_task(self, task):
        await self._log(f"🚀 Initializing Swarm Protocol for task: {task}")
        plan = await self._plan(task)

        for idx, step in enumerate(plan):
            await self._log(f"--- Step {idx+1}/{len(plan)} ---")
            await self.execute_step(step)

        await self._log("🏁 Task execution completed.")
