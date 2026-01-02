from asgiref.sync import async_to_sync
from celery import shared_task

from base.models import WebpageScreenshot


@shared_task
def save_initial_screenshot(webpage_id: int) -> None:
    """
    Celery task to save initial screenshot for a webpage
    """
    async_to_sync(WebpageScreenshot.save_screenshot)(webpage_id)
