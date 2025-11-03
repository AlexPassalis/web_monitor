from playwright.sync_api import Browser
from imagehash import ImageHash

import io

from PIL import Image
import imagehash


def get_screenshot_perceptual_hash(browser: Browser, url: str) -> tuple[ImageHash, bytes]:
    """
    Take screenshot of URL and return perceptual hash + screenshot bytes.
    """

    page = browser.new_page()
    page.goto(url, wait_until='networkidle', timeout=30000)

    screenshot_bytes = page.screenshot(full_page=True)

    image = Image.open(io.BytesIO(screenshot_bytes))
    perceptual_hash = imagehash.phash(image)

    page.close()

    return perceptual_hash, screenshot_bytes
