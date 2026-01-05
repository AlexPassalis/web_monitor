from asgiref.sync import async_to_sync
from celery import shared_task

from base.models import WebpageScreenshot
from config.utils import browser_cleanup


@shared_task
def save_initial_screenshot(webpage_id: int) -> None:
    """
    Celery task to save initial screenshot for a webpage
    """

    async def run():
        try:
            await WebpageScreenshot.save_screenshot(webpage_id)
        finally:
            await browser_cleanup()

    async_to_sync(run)()
