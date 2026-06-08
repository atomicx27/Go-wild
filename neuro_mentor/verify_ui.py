import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(record_video_dir=".")
        page = await context.new_page()

        # Go to app
        await page.goto("http://localhost:8000")

        # Wait for the scanning/enabling UI
        await page.wait_for_timeout(2000)

        # Take initial screenshot of UI layout with "No Module Selected" state
        await page.screenshot(path="neuro_mentor_initial.png")

        # We assume the background agent won't instantly process anything since Ollama might take a while
        # For the sake of UI verification, we'll just check the frontend layout.

        # Close
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
