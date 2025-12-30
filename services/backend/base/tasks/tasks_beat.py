import logging

from celery import shared_task

from base.models import Webpage, WebpageScreenshot

logger = logging.getLogger(__name__)


@shared_task
def run_every_minute() -> None:
    """
    Celery task that runs every minute
    """
    webpages = Webpage.objects.exclude(minute__isnull=True).distinct()
    if not webpages.exists():
        logger.info('There are no webpages being tracked every minute')
        return

    for webpage in webpages:
        WebpageScreenshot.save_screenshot.apply_async(
            args=(webpage.id,),
            queue='high_priority',
        )
