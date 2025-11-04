from imagehash import ImageHash

import asyncio
import logging

from asgiref.sync import async_to_sync
from celery import shared_task

from playwright.async_api import async_playwright
from base.models import TrackedWebsite
from base.utils import async_get_screenshot_perceptual_hash

logger = logging.getLogger(__name__)


async def async_run_every_minute(tracked_websites: list[TrackedWebsite]) -> None:
    """Async implementation with concurrent screenshot processing."""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        tasks = []
        for tracked_website in tracked_websites:
            task = async_get_screenshot_perceptual_hash(browser, tracked_website.url)
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        await browser.close()

    html_contents: dict[int, tuple[ImageHash, bytes]] = {}
    for i, tracked_website in enumerate(tracked_websites):
        html_contents[tracked_website.id] = results[i]

    for tracked_website in tracked_websites:
        perpetual_hash, screenshot_bytes = html_contents[tracked_website.id]
        print(perpetual_hash)


@shared_task
def run_every_minute() -> None:
    """Celery task that runs every minute."""

    tracked_websites_qs = TrackedWebsite.objects.exclude(minute__isnull=True).distinct()
    if not tracked_websites_qs.exists():
        logger.info('There are no websites being tracked every minute.')
        return

    tracked_websites = list(tracked_websites_qs)
    async_to_sync(async_run_every_minute)(tracked_websites)


#        latest_snapshot = tracked_website.get_latest_snapshot()
#        if latest_snapshot is None or latest_snapshot.html_content != html_content:
#            WebsiteSnapshot.objects.create(
#                tracked_website=tracked_website,
#                html_content=html_content,
#            )
#            logger.info(f'New snapshot created for {tracked_website.url}')
#        else:
#            logger.info(f'No changes detected for {tracked_website.url}')


@shared_task
def run_every_hour() -> None:
    """Celery task that runs every hour."""

    logger.info('There are no websites being tracked every hour.')
    pass


@shared_task
def run_every_day() -> None:
    """Celery task that runs every day."""

    logger.info('There are no websites being tracked every day.')
    pass
