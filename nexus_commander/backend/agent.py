import re
import json
from .ollama_client import generate_chat_stream, generate_chat
from .tools import execute_bash

SYSTEM_PROMPT = """You are Nexus Commander, an autonomous AI agent capable of executing bash commands to solve tasks.
You operate in a ReAct (Reasoning and Acting) loop.

For EVERY turn, you MUST output your response exactly in this format using the following XML tags:

<THINK>
Write your reasoning here. What are you trying to do? What command do you need to run?
</THINK>
<EXECUTE>
The bash command to run. (Do not include markdown formatting or backticks around the command itself inside this tag).
</EXECUTE>

When you are completely finished with the task and have the final answer, output:
<THINK>
I have the final answer.
</THINK>
<ANSWER>
Your detailed final response to the user's initial request.
</ANSWER>

Rules:
1. You can only use <EXECUTE> OR <ANSWER> in a single response, NEVER both.
2. If you use <EXECUTE>, the system will run the command and provide you with the output in the next turn.
3. Be careful with commands. You are running on a real machine.
4. Always explore the environment first if you aren't sure where files are.
"""

def parse_agent_response(response_text: str):
    """
    Parses the agent's response to extract THINK, EXECUTE, and ANSWER blocks.
    """
    think_match = re.search(r"<THINK>(.*?)</THINK>", response_text, re.DOTALL)
    execute_match = re.search(r"<EXECUTE>(.*?)</EXECUTE>", response_text, re.DOTALL)
    answer_match = re.search(r"<ANSWER>(.*?)</ANSWER>", response_text, re.DOTALL)

    return {
        "think": think_match.group(1).strip() if think_match else None,
        "execute": execute_match.group(1).strip() if execute_match else None,
        "answer": answer_match.group(1).strip() if answer_match else None,
        "raw": response_text
    }

async def run_agent_loop(task: str, websocket=None):
    """
    Runs the ReAct loop until an ANSWER is generated or max iterations reached.
    If websocket is provided, streams the progress.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Task: {task}"}
    ]

    max_iterations = 15

    for i in range(max_iterations):
        if websocket:
            await websocket.send_text(json.dumps({"type": "status", "content": f"Iteration {i+1}..."}))

        # Stream the response
        full_response = ""
        current_block = None

        if websocket:
            await websocket.send_text(json.dumps({"type": "stream_start"}))
            async for chunk in generate_chat_stream(messages):
                if "message" in chunk and "content" in chunk["message"]:
                    content = chunk["message"]["content"]
                    full_response += content

                    # Very basic streaming logic for UI
                    # We send chunks to the frontend as they come
                    await websocket.send_text(json.dumps({
                        "type": "stream_chunk",
                        "content": content,
                        "full": full_response
                    }))
                elif "error" in chunk:
                    if websocket:
                         await websocket.send_text(json.dumps({"type": "error", "content": chunk["error"]}))
                    return
            if websocket:
                 await websocket.send_text(json.dumps({"type": "stream_end"}))
        else:
            # Non-streaming for testing
            response = await generate_chat(messages)
            if "message" in response:
                full_response = response["message"]["content"]
            else:
                 return "Error in generation"

        messages.append({"role": "assistant", "content": full_response})
        parsed = parse_agent_response(full_response)

        if websocket and parsed["think"]:
            await websocket.send_text(json.dumps({"type": "think", "content": parsed["think"]}))

        if parsed["answer"]:
            if websocket:
                await websocket.send_text(json.dumps({"type": "answer", "content": parsed["answer"]}))
            return parsed["answer"]

        elif parsed["execute"]:
            command = parsed["execute"]
            if websocket:
                await websocket.send_text(json.dumps({"type": "execute", "content": command}))

            output = execute_bash(command)

            if websocket:
                await websocket.send_text(json.dumps({"type": "command_output", "content": output}))

            messages.append({"role": "user", "content": f"Command output:\n{output}"})
        else:
            # Malformed output
            error_msg = "Error: Invalid output format. You must provide either <EXECUTE> or <ANSWER> along with <THINK>."
            messages.append({"role": "user", "content": error_msg})
            if websocket:
                 await websocket.send_text(json.dumps({"type": "error", "content": error_msg}))

    if websocket:
        await websocket.send_text(json.dumps({"type": "error", "content": "Max iterations reached without an answer."}))
    return "Max iterations reached."
