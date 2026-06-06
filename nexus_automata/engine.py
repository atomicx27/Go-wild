import asyncio
import json
import httpx
import subprocess
from pathlib import Path
from database import update_run_logs, get_workflow

OLLAMA_API_URL = "http://localhost:11434/api/chat"

async def call_ollama(prompt: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OLLAMA_API_URL,
                json={
                    "model": "llama3",
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
                },
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
    except Exception as e:
        return f"Error calling Ollama: {str(e)}"

async def execute_step(step: dict, context: dict, run_id: int):
    step_id = step.get("id")
    step_type = step.get("type")
    content = step.get("content")

    # Replace variables in content like {{prev_output}}
    for key, value in context.items():
        if isinstance(value, str):
            content = content.replace(f"{{{{{key}}}}}", value)

    update_run_logs(run_id, f"--- Starting Step: {step_id} ({step_type}) ---")
    update_run_logs(run_id, f"Content:\n{content}\n")

    result_output = ""

    try:
        if step_type == "shell":
            process = await asyncio.create_subprocess_shell(
                content,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="nexus_automata/workdir"
            )
            stdout, stderr = await process.communicate()
            if stdout:
                result_output += stdout.decode()
            if stderr:
                result_output += stderr.decode()

        elif step_type == "ai":
            result_output = await call_ollama(content)

        elif step_type == "write_file":
            target = step.get("target")
            if not target:
                result_output = "Error: target path not specified for write_file"
            else:
                file_path = Path("nexus_automata/workdir") / target
                # Ensure parent dir exists safely
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                result_output = f"Successfully wrote to {target}"
        else:
            result_output = f"Unknown step type: {step_type}"

    except Exception as e:
        result_output = f"Exception during execution: {str(e)}"

    update_run_logs(run_id, f"Result:\n{result_output}\n")
    return result_output

async def run_workflow(run_id: int, workflow_id: int):
    # Ensure workdir exists
    Path("nexus_automata/workdir").mkdir(parents=True, exist_ok=True)

    workflow = get_workflow(workflow_id)
    if not workflow:
        update_run_logs(run_id, "Error: Workflow not found.", status="failed")
        return

    update_run_logs(run_id, f"Starting Workflow ID {workflow_id}: {workflow['goal']}")

    try:
        steps = json.loads(workflow["steps_json"])
    except json.JSONDecodeError:
        update_run_logs(run_id, "Error: Invalid JSON in steps.", status="failed")
        return

    context = {}

    # Very basic linear execution for now (ignoring depends_on for simplicity in the PoC)
    for step in steps:
        output = await execute_step(step, context, run_id)
        # Store output in context with step id
        context[f"output_{step.get('id')}"] = output
        # Also store generically as prev_output
        context["prev_output"] = output

    update_run_logs(run_id, "Workflow completed successfully.", status="completed")
