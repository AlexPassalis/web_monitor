import asyncio
import logging
import threading
from typing import TypedDict

import playwright.async_api

logger = logging.getLogger(__name__)


class BrowserData(TypedDict):
    p: playwright.async_api.Playwright
    browser: playwright.async_api.Browser
    loop_id: int


browser_data: BrowserData | None = None
dict_lock = threading.Lock()
async_locks: dict[asyncio.AbstractEventLoop, asyncio.Lock] = {}


async def get_browser() -> playwright.async_api.Browser:
    global browser_data

    current_loop = asyncio.get_running_loop()
    current_loop_id = id(current_loop)

    with dict_lock:
        if current_loop not in async_locks:
            async_locks[current_loop] = asyncio.Lock()
        lock = async_locks[current_loop]

    async with lock:
        if browser_data is not None:
            if browser_data.get('loop_id') != current_loop_id:
                browser_data = None
            elif browser_data['browser'].is_connected():
                return browser_data['browser']
            else:
                browser_data = None

        p = await playwright.async_api.async_playwright().start()
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage'],
        )

        browser_data = {'p': p, 'browser': browser, 'loop_id': current_loop_id}
        logger.info('New browser instance created for loop %s', current_loop_id)

        return browser


async def browser_cleanup() -> None:
    global browser_data

    current_loop = asyncio.get_running_loop()
    current_loop_id = id(current_loop)

    with dict_lock:
        async_locks.pop(current_loop, None)
        if browser_data is not None:
            if browser_data.get('loop_id') == current_loop_id:
                try:
                    await browser_data['browser'].close()
                    await browser_data['p'].stop()
                    logger.info('Browser instance closed for loop %s', current_loop_id)
                finally:
                    browser_data = None
