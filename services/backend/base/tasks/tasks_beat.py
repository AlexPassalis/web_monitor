import asyncio
import logging

from asgiref.sync import async_to_sync
from celery import shared_task

from base.models import WebpageMonitoring, WebpageScreenshot
from config.utils import browser_cleanup

logger = logging.getLogger(__name__)


@shared_task
def run_every_minute() -> None:
    """
    Celery task that runs every minute
    """
    webpage_ids = (
        WebpageMonitoring.objects.filter(interval='minute')
        .values_list('webpage_id', flat=True)
        .distinct()
    )

    if not webpage_ids:
        logger.info('There are no webpages being monitored every minute')
        return

    async def run_all():
        try:
            tasks = []
            for webpage_id in webpage_ids:
                tasks.append(WebpageScreenshot.save_screenshot(webpage_id))
            return await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=50,
            )
        finally:
            await browser_cleanup()

    results = async_to_sync(run_all)()
    for result in results:
        if isinstance(result, BaseException):
            raise result
