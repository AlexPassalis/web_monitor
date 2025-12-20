import datetime
import io
import logging

import celery
import django.core.files.base
import django.core.files.storage
import imagehash
import PIL.Image
import playwright.sync_api

from base.models import WebpageScreenshot

logger = logging.getLogger(__name__)


@celery.shared_task
def create_initial_webpagescreenshot(tracked_webpage_id: int, tracked_webpage_url: str) -> None:
    """
    Create the initial Webpagescreenshot for a newly tracked webpage
    """

    with playwright.sync_api.sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        perceptual_hash, webpagescreenshot = take_webpagescreenshot(
            browser,
            url=tracked_webpage_url,
        )
        browser.close()

    timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
    file_path = f'webpagescreenshots/{tracked_webpage_id}/{timestamp}.png'

    upload_webpagescreenshot(webpagescreenshot, file_path)

    WebpageScreenshot.objects.create(
        tracked_webpage_id=tracked_webpage_id,
        perceptual_hash=str(perceptual_hash),
    )


def take_webpagescreenshot(
    browser: playwright.sync_api.Browser, url: str
) -> tuple[imagehash.ImageHash, bytes]:
    """
    Take screenshot of webpage and return perceptual hash + screenshot
    """

    page = browser.new_page()
    page.goto(url, wait_until='networkidle', timeout=30000)

    screenshot = page.screenshot(full_page=True)

    image = PIL.Image.open(io.BytesIO(screenshot))
    perceptual_hash = imagehash.phash(image)

    page.close()

    return perceptual_hash, screenshot


def upload_webpagescreenshot(webpagescreenshot: bytes, file_path: str) -> None:
    """
    Upload screenshot of webpage to S3 bucket
    """

    django.core.files.storage.default_storage.save(
        name=file_path,
        content=django.core.files.base.ContentFile(content=webpagescreenshot),
    )
