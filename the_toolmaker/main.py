import argparse
import subprocess
import os
import sys

# Ensure imports work regardless of how script is called
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from the_toolmaker.llm_logic import analyze_request, forge_tool, plan_execution
from the_toolmaker.registry import get_tool

def execute_command(command):
    """Executes a shell command and prints its output."""
    print(f"\n[Toolmaker] Executing: {command}\n")
    print("-" * 40)
    try:
        # Change directory to the repository root so relative paths work
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        result = subprocess.run(command, shell=True, check=True, text=True, cwd=repo_root)
    except subprocess.CalledProcessError as e:
        print(f"\n[Toolmaker Error] Command failed with return code {e.returncode}")
    print("-" * 40)

def handle_request(user_request):
    """Core logic to process a single user request."""
    print(f"\n[Toolmaker] Analyzing request: '{user_request}'")

    analysis = analyze_request(user_request)
    action = analysis.get("action")
    tool_name = analysis.get("tool_name", "fallback_tool")

    tool_filepath = None

    if action == "use_existing":
        print(f"[Toolmaker] Decided to use existing tool: {tool_name}")
        tool_info = get_tool(tool_name)
        if tool_info:
            tool_filepath = tool_info["filepath"]
        else:
            print(f"[Toolmaker Error] Tool '{tool_name}' found in analysis but not in registry. Forging new tool.")
            action = "create_new"

    if action == "create_new":
        print(f"[Toolmaker] Decided to forge a new tool: {tool_name}")
        tool_filepath = forge_tool(tool_name, user_request)
        if not tool_filepath:
            print("[Toolmaker Error] Failed to forge tool.")
            return

    if tool_filepath:
        print(f"[Toolmaker] Planning execution for tool: {tool_filepath}")
        command = plan_execution(tool_filepath, user_request)

        # Simple safety check: ensure the command at least tries to run python
        if not command.startswith("python"):
             command = f"python3 {tool_filepath}"

        execute_command(command)

def interactive_mode():
    """Runs a REPL loop for continuous interaction."""
    print("Welcome to The Toolmaker Interactive Mode.")
    print("Type your request or 'exit' to quit.")
    print("=" * 50)

    while True:
        try:
            user_input = input("\nToolmaker> ")
            if user_input.lower() in ['exit', 'quit']:
                break
            if not user_input.strip():
                continue

            handle_request(user_input)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="The Toolmaker - An autonomous agent that creates and runs tools.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: do
    do_parser = subparsers.add_parser("do", help="Execute a specific request")
    do_parser.add_argument("request", type=str, help="The task you want The Toolmaker to perform")

    # Command: interactive
    subparsers.add_parser("interactive", help="Start interactive REPL mode")

    args = parser.parse_args()

    if args.command == "do":
        handle_request(args.request)
    elif args.command == "interactive":
        interactive_mode()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
