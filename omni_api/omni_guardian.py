import subprocess
import time
import os
import omni_healer

def run_guardian():
    print("[Guardian] Starting Omni Guardian Watchdog...")

    while True:
        print("[Guardian] Starting Uvicorn subprocess...")
        # Start uvicorn as a subprocess. We don't use --reload because we want to manage restarts ourselves
        # if there's a hard crash (like syntax error). But we DO want reload so it picks up endpoints.py changes.
        # Actually, if we use --reload, uvicorn might crash its reloader if there's a syntax error.
        # Let's run uvicorn. If it exits with non-zero, we catch it.

        process = subprocess.Popen(
            ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True
        )

        # We need a way to read output without blocking forever if the server is running normally.
        # But we also want to see if it crashed immediately due to a syntax error.

        while True:
            # Check if process is still running
            retcode = process.poll()

            if retcode is not None:
                # Process exited!
                print(f"[Guardian] Uvicorn process exited with code {retcode}")
                if retcode != 0:
                    # It crashed. Read stderr.
                    stderr_output = process.stderr.read()
                    print(f"[Guardian] Uvicorn crashed. Error:\n{stderr_output}")

                    if "SyntaxError" in stderr_output or "ImportError" in stderr_output or "NameError" in stderr_output or "IndentationError" in stderr_output or "Exception" in stderr_output:
                        print("[Guardian] Detected syntax or import error. Calling Healer...")
                        omni_healer.fix_syntax_error(stderr_output)
                        print("[Guardian] Healer finished. Waiting 2 seconds before restarting...")
                        time.sleep(2)
                    else:
                        print("[Guardian] Unknown crash. Restarting in 5 seconds...")
                        time.sleep(5)
                break # Break out of inner loop to restart

            # If still running, sleep briefly
            time.sleep(1)

if __name__ == "__main__":
    run_guardian()
