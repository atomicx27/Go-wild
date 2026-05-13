import os
import shutil
import subprocess
import time
from llm import generate_text, extract_code
from prompts import (
    SPARTACUS_SYSTEM_PROMPT, CRIXUS_SYSTEM_PROMPT, CAESAR_SYSTEM_PROMPT,
    get_code_prompt, get_test_prompt, get_judge_prompt
)

ARENA_DIR = "arena"
CHALLENGES_DIR = "challenges"
COMPLETED_DIR = os.path.join(CHALLENGES_DIR, "completed")
BATTLES_DIR = "battles"

def setup_arena():
    """Clears and prepares the arena directory."""
    if os.path.exists(ARENA_DIR):
        shutil.rmtree(ARENA_DIR)
    os.makedirs(ARENA_DIR)

def get_pending_challenges():
    """Gets a list of challenge files."""
    if not os.path.exists(CHALLENGES_DIR):
        os.makedirs(CHALLENGES_DIR)
    files = [f for f in os.listdir(CHALLENGES_DIR) if os.path.isfile(os.path.join(CHALLENGES_DIR, f)) and f.endswith(".txt")]
    return [os.path.join(CHALLENGES_DIR, f) for f in files]

def run_pytest(test_file):
    """Runs pytest on a given file and returns the output."""
    try:
        result = subprocess.run(["pytest", test_file, "-v"], capture_output=True, text=True, cwd=ARENA_DIR, timeout=10)
        return f"Return Code: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "Return Code: -1\n\nResult: TIMEOUT"
    except Exception as e:
        return f"Return Code: -1\n\nResult: ERROR: {e}"

def extract_html(text):
    """Extracts HTML blocks from text."""
    if "```html" in text:
        parts = text.split("```html")
        if len(parts) > 1:
            return parts[1].split("```")[0].strip()
    return text.strip()

def host_battle(challenge_file):
    setup_arena()

    challenge_name = os.path.basename(challenge_file).replace('.txt', '')
    print(f"\n[⚔️ ] Hosting Battle: {challenge_name} [⚔️ ]")

    with open(challenge_file, "r") as f:
        challenge_text = f.read()

    code_prompt = get_code_prompt(challenge_text)

    # PHASE 1: Code Generation
    print("[1] Spartacus is writing code...")
    spartacus_raw = generate_text(code_prompt, SPARTACUS_SYSTEM_PROMPT)
    spartacus_code = extract_code(spartacus_raw)
    with open(os.path.join(ARENA_DIR, "spartacus.py"), "w") as f:
        f.write(spartacus_code)

    print("[1] Crixus is writing code...")
    crixus_raw = generate_text(code_prompt, CRIXUS_SYSTEM_PROMPT)
    crixus_code = extract_code(crixus_raw)
    with open(os.path.join(ARENA_DIR, "crixus.py"), "w") as f:
        f.write(crixus_code)

    # PHASE 2: Test Generation
    print("[2] Spartacus is writing tests for Crixus...")
    s_test_prompt = get_test_prompt("crixus", crixus_code)
    s_test_raw = generate_text(s_test_prompt, SPARTACUS_SYSTEM_PROMPT)
    s_test_code = extract_code(s_test_raw)
    with open(os.path.join(ARENA_DIR, "test_crixus.py"), "w") as f:
        f.write(s_test_code)

    print("[2] Crixus is writing tests for Spartacus...")
    c_test_prompt = get_test_prompt("spartacus", spartacus_code)
    c_test_raw = generate_text(c_test_prompt, CRIXUS_SYSTEM_PROMPT)
    c_test_code = extract_code(c_test_raw)
    with open(os.path.join(ARENA_DIR, "test_spartacus.py"), "w") as f:
        f.write(c_test_code)

    # PHASE 3: Cross Testing
    print("[3] Running tests...")
    print("    - Crixus's code vs Spartacus's tests...")
    s_test_c_result = run_pytest("test_crixus.py")

    print("    - Spartacus's code vs Crixus's tests...")
    c_test_s_result = run_pytest("test_spartacus.py")

    # PHASE 4: Judgment
    print("[4] Caesar is judging the outcome...")
    judge_prompt = get_judge_prompt(spartacus_code, crixus_code, s_test_c_result, c_test_s_result)
    caesar_raw = generate_text(judge_prompt, CAESAR_SYSTEM_PROMPT)
    html_report = extract_html(caesar_raw)

    # Save results
    timestamp = int(time.time())
    battle_dir = os.path.join(BATTLES_DIR, f"{challenge_name}_{timestamp}")
    os.makedirs(battle_dir, exist_ok=True)

    with open(os.path.join(battle_dir, "report.html"), "w") as f:
        f.write(html_report)
    shutil.copy2(os.path.join(ARENA_DIR, "spartacus.py"), os.path.join(battle_dir, "spartacus.py"))
    shutil.copy2(os.path.join(ARENA_DIR, "crixus.py"), os.path.join(battle_dir, "crixus.py"))

    # Move challenge to completed
    shutil.move(challenge_file, os.path.join(COMPLETED_DIR, os.path.basename(challenge_file)))

    print(f"[✅] Battle complete! Report saved to: {battle_dir}/report.html")

def main():
    challenges = get_pending_challenges()
    if not challenges:
        print("No pending challenges found in the arena.")
        return

    for challenge in challenges:
        host_battle(challenge)

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs(ARENA_DIR, exist_ok=True)
    os.makedirs(CHALLENGES_DIR, exist_ok=True)
    os.makedirs(COMPLETED_DIR, exist_ok=True)
    os.makedirs(BATTLES_DIR, exist_ok=True)
    main()
