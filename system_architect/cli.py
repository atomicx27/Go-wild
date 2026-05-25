import argparse
import sys
from .core import Architect

def main():
    parser = argparse.ArgumentParser(
        description="\033[36mSystem Architect\033[0m: Autonomous AI Project Scaffolder",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "project_name",
        help="The name of the project directory to create within the blueprints folder."
    )
    parser.add_argument(
        "prompt",
        help="The description of the project to generate (e.g., 'A simple python hello world package')."
    )
    parser.add_argument(
        "--model",
        default="llama3",
        help="The Ollama model to use (default: llama3)."
    )
    parser.add_argument(
        "--outdir",
        default="system_architect/blueprints",
        help="The base directory to generate the project in (default: system_architect/blueprints)."
    )

    args = parser.parse_args()

    print(f"\n\033[1;35m[SYSTEM ARCHITECT]\033[0m Initializing...")
    print(f"\033[90mTarget Project:\033[0m {args.project_name}")
    print(f"\033[90mModel:\033[0m {args.model}")
    print(f"\033[90mPrompt:\033[0m {args.prompt}\n")

    architect = Architect(output_dir=args.outdir, model=args.model)

    try:
        architect.run(args.prompt, args.project_name)
    except Exception as e:
        print(f"\n\033[1;31m[CRITICAL ERROR]\033[0m {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
