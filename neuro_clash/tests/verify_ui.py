from playwright.sync_api import sync_playwright

def verify_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:8000/static/index.html")

        # Take initial screenshot
        page.screenshot(path="neuro_clash/tests/ui_initial.png")

        # Fill in topic and click start
        page.fill("#topicInput", "Is simulation theory real?")
        page.click("#startBtn")

        # Wait a bit for the debate to start and UI to update
        page.wait_for_timeout(2000)

        # Take screenshot of active debate
        page.screenshot(path="neuro_clash/tests/ui_active.png")

        browser.close()

if __name__ == "__main__":
    verify_frontend()
