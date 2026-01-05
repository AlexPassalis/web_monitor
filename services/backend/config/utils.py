import asyncio
import logging
import threading
from typing import Callable, TypedDict

import playwright.async_api
from django.db import connection

logger = logging.getLogger(__name__)


class BrowserData(TypedDict):
    p: playwright.async_api.Playwright
    browser: playwright.async_api.Browser


browser_data: dict[int, BrowserData] = {}
async_locks: dict[int, asyncio.Lock] = {}
global_lock = threading.Lock()


async def get_browser() -> playwright.async_api.Browser:
    """
    Get or create a browser for the current event loop.
    """
    loop_id = id(asyncio.get_running_loop())

    with global_lock:
        if loop_id not in async_locks:
            async_locks[loop_id] = asyncio.Lock()
        lock = async_locks[loop_id]

    async with lock:
        if loop_id in browser_data and browser_data[loop_id]['browser'].is_connected():
            return browser_data[loop_id]['browser']

        p = await playwright.async_api.async_playwright().start()
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage'],
        )

        browser_data[loop_id] = {'p': p, 'browser': browser}
        logger.info('New browser instance created for loop %s', loop_id)
        return browser


async def browser_cleanup() -> None:
    """
    Close the browser for the current event loop.
    """
    loop_id = id(asyncio.get_running_loop())

    with global_lock:
        data = browser_data.pop(loop_id, None)
        async_locks.pop(loop_id, None)

    if data is not None:
        await data['browser'].close()
        await data['p'].stop()
        logger.info('Browser instance closed for loop %s', loop_id)


def with_connection_cleanup[**Params, Return](
    func: Callable[Params, Return],
) -> Callable[Params, Return]:
    """
    Wraps a function to close the database connection after execution.
    Use this when running Django ORM operations in separate threads via asyncio.to_thread.
    """

    def wrapper(*args: Params.args, **kwargs: Params.kwargs) -> Return:
        try:
            return func(*args, **kwargs)
        finally:
            connection.close()

    return wrapper
