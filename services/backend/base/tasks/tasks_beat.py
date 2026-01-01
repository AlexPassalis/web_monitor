import logging

from celery import shared_task

from base.models import WebpageScreenshot, WebpageTracking

logger = logging.getLogger(__name__)


@shared_task
def run_every_minute() -> None:
    """
    Celery task that runs every minute
    """
    webpage_ids = (
        WebpageTracking.objects.filter(interval='minute')
        .values_list('webpage_id', flat=True)
        .distinct()
    )

    if not webpage_ids:
        logger.info('There are no webpages being tracked every minute')
        return

    for webpage_id in webpage_ids:
        WebpageScreenshot.save_screenshot.apply_async(
            args=(webpage_id,),
            queue='high_priority',
        )
