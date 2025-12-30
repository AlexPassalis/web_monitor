import asyncio
from typing import TypedDict

import playwright.async_api


class BrowserData(TypedDict):
    p: playwright.async_api.Playwright
    browser: playwright.async_api.Browser


EVENT_LOOPS: dict[asyncio.AbstractEventLoop, BrowserData] = {}


async def get_browser() -> playwright.async_api.Browser:
    """
    Get or create the shared browser instance
    """
    global EVENT_LOOPS

    current_loop = asyncio.get_running_loop()
    data = EVENT_LOOPS.get(current_loop)
    if data and data['browser'].is_connected():
        return data['browser']

    p = await playwright.async_api.async_playwright().start()
    browser = await p.chromium.launch(
        headless=True, args=['--no-sandbox', '--disable-dev-shm-usage']
    )
    EVENT_LOOPS[current_loop] = {'p': p, 'browser': browser}

    return browser
