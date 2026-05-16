import requests
import time
import subprocess
import os
import signal

def demo():
    print("--- Omni API Demo ---")

    # Check if server is running
    print("\n1. Testing root (should exist):")
    try:
        res = requests.get("http://localhost:8000/")
        print(f"Status: {res.status_code}, Response: {res.json()}")
    except requests.exceptions.ConnectionError:
        print("Server not running. Start it with `python omni_guardian.py` in the omni_api directory.")
        return

    # 2. Test generating a 404
    print("\n2. Requesting a non-existent endpoint (GET /magic/potion):")
    res = requests.get("http://localhost:8000/magic/potion")
    print(f"Status: {res.status_code}, Response: {res.json()}")

    print("Waiting 20 seconds for Healer to generate code, write to endpoints.py, and Uvicorn to auto-reload...")
    time.sleep(20)

    # 3. Test again
    print("\n3. Requesting the newly generated endpoint (GET /magic/potion):")
    try:
        res = requests.get("http://localhost:8000/magic/potion")
        print(f"Status: {res.status_code}")
        try:
            print(f"Response: {res.json()}")
        except Exception:
            print(f"Response text: {res.text}")
    except requests.exceptions.ConnectionError:
        print("Server crashed and hasn't restarted yet.")

if __name__ == "__main__":
    demo()
