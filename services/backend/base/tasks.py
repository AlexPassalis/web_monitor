import logging

from celery import shared_task
from playwright.sync_api import sync_playwright

from base.models import WebsiteScreenshot
from base.utils import sync_get_screenshot_perceptual_hash

logger = logging.getLogger(__name__)


@shared_task
def create_initial_screenshot(tracked_website_id: int, tracked_website_url: str) -> None:
    """Create the first screenshot for a newly tracked website."""

    logger.info(f'Creating initial screenshot for {tracked_website_url}')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        perceptual_hash, screenshot_bytes = sync_get_screenshot_perceptual_hash(
            browser,
            tracked_website_url,
        )
        browser.close()

    WebsiteScreenshot.objects.create(
        tracked_website_id=tracked_website_id,
        perceptual_hash=str(perceptual_hash),
    )

    logger.info(f'Initial screenshot created for {tracked_website_url}')
