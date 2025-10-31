import logging

from celery import shared_task

from playwright.sync_api import sync_playwright
from base.models import TrackedWebsite, WebsiteSnapshot
from base.utils import get_html_content

logger = logging.getLogger(__name__)


@shared_task
def run_every_minute():
    """Celery task that runs every minute."""

    tracked_websites = TrackedWebsite.objects.exclude(minute__isnull=True).distinct()
    if not tracked_websites.exists():
        logger.info('No tracked websites for every minute task.')
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for tracked_website in tracked_websites:
            html_content = get_html_content(browser, tracked_website.url)
            latest_snapshot = tracked_website.get_latest()
            if latest_snapshot.html_content != html_content:
                WebsiteSnapshot.objects.create(
                    tracked_website=tracked_website,
                    html_content=html_content,
                )
                logger.info(f'New snapshot created for {tracked_website.url}')
            else:
                logger.info(f'No changes detected for {tracked_website.url}')
        browser.close()


@shared_task
def run_every_hour():
    """Celery task that runs every hour."""

    logger.info('Task running every hour')
    pass


@shared_task
def run_every_day():
    """Celery task that runs every day."""

    logger.info('Task running every day')
    pass
