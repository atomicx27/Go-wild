import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        await page.goto("http://localhost:3000")

        # Take initial screenshot
        await page.screenshot(path="/home/jules/verification/overdrive_initial.png")

        # Simulate an interaction
        await page.fill("#topic-input", "Conscious Toasters")
        await page.click("#start-btn")

        # Wait a moment for UI to change state
        await asyncio.sleep(2)
        await page.screenshot(path="/home/jules/verification/overdrive_active.png")

        await browser.close()

asyncio.run(run())
