import logging

from celery import shared_task
from playwright.sync_api import sync_playwright

from base.models import WebsiteSnapshot
from base.utils import get_html_content

logger = logging.getLogger(__name__)


@shared_task
def create_initial_snapshot(tracked_website_id: int, tracked_website_url: str) -> None:
    """Create the first snapshot for a newly tracked website."""

    logger.info(f'Creating initial snapshot for {tracked_website_url}')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        html_content = get_html_content(browser, tracked_website_url)
        browser.close()

    WebsiteSnapshot.objects.create(
        tracked_website_id=tracked_website_id,
        html_content=html_content,
    )

    logger.info(f'Initial snapshot created for {tracked_website_url}')
