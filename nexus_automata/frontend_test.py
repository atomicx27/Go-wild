from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(record_video_dir=".")
        page = context.new_page()

        # Navigate to UI
        page.goto("http://localhost:8000")
        time.sleep(2)

        # Take a screenshot of the empty state
        page.screenshot(path="screenshot.png")

        # Assuming Ollama is not actually running in test sandbox, so generating might fail or take too long,
        # but we can try to type into the input at least to record it.
        page.fill("#goalInput", "Write a python script that prints hello world")
        time.sleep(1)

        page.screenshot(path="screenshot2.png")

        context.close()
        browser.close()

if __name__ == "__main__":
    run()
