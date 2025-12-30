import asyncio
import logging
from typing import TypedDict

import playwright.async_api

logger = logging.getLogger(__name__)


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
    if data:
        if data['browser'].is_connected():
            return data['browser']
        else:
            await data['browser'].close()
            await data['p'].stop()
            del EVENT_LOOPS[current_loop]
            logger.info('Removed disconnected browser instance for loop %s', current_loop)

    p = await playwright.async_api.async_playwright().start()
    browser = await p.chromium.launch(
        headless=True, args=['--no-sandbox', '--disable-dev-shm-usage']
    )
    EVENT_LOOPS[current_loop] = {'p': p, 'browser': browser}

    logger.info('Created new browser instance for event loop %s', current_loop)
    logger.info('Total browser instances: %d', len(EVENT_LOOPS))

    return browser
