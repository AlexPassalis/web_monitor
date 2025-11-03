import logging

from celery import shared_task

from playwright.sync_api import sync_playwright
from base.models import TrackedWebsite, WebsiteSnapshot
from base.utils import get_html_content

logger = logging.getLogger(__name__)


@shared_task
def run_every_minute() -> None:
    """Celery task that runs every minute."""

    tracked_websites_qs = TrackedWebsite.objects.exclude(minute__isnull=True).distinct()
    if not tracked_websites_qs.exists():
        logger.info('No tracked websites for every minute task.')
        return

    tracked_websites = list(tracked_websites_qs)
    html_contents: dict[int, str] = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for tracked_website in tracked_websites:
            html_contents[tracked_website.id] = get_html_content(browser, tracked_website.url)
        browser.close()

    for tracked_website in tracked_websites:
        html_content = html_contents[tracked_website.id]
        latest_snapshot = tracked_website.get_latest_snapshot()
        if latest_snapshot is None or latest_snapshot.html_content != html_content:
            WebsiteSnapshot.objects.create(
                tracked_website=tracked_website,
                html_content=html_content,
            )
            logger.info(f'New snapshot created for {tracked_website.url}')
        else:
            logger.info(f'No changes detected for {tracked_website.url}')


@shared_task
def run_every_hour() -> None:
    """Celery task that runs every hour."""

    logger.info('Task running every hour')
    pass


@shared_task
def run_every_day() -> None:
    """Celery task that runs every day."""

    logger.info('Task running every day')
    pass
