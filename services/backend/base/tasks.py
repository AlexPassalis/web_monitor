import logging
from datetime import datetime

from celery import shared_task
from playwright.sync_api import sync_playwright

from base.models import WebsiteScreenshot
from base.utils import sync_get_screenshot_perceptual_hash
from config.s3 import upload_file, ensure_bucket_exists

logger = logging.getLogger(__name__)


@shared_task
def create_initial_screenshot(tracked_website_id: int, tracked_website_url: str) -> None:
    """Create the first screenshot for a newly tracked website."""

    logger.info(f'Creating initial screenshot for {tracked_website_url}')

    ensure_bucket_exists()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        perceptual_hash, screenshot_bytes = sync_get_screenshot_perceptual_hash(
            browser,
            tracked_website_url,
        )
        browser.close()

    timestamp = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
    s3_key = f'screenshots/{tracked_website_id}/{timestamp}.png'

    upload_file(screenshot_bytes, s3_key, content_type='image/png')

    WebsiteScreenshot.objects.create(
        tracked_website_id=tracked_website_id,
        perceptual_hash=str(perceptual_hash),
        s3_key=s3_key,
    )

    logger.info(f'Initial screenshot created for {tracked_website_url}')
