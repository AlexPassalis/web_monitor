from base.models import TrackedWebsite, WebsiteScreenshot
from imagehash import ImageHash

import asyncio
import logging
from datetime import datetime

from asgiref.sync import async_to_sync, sync_to_async
from celery import shared_task

from playwright.async_api import async_playwright
from base.utils import async_get_screenshot_perceptual_hash
from config.s3 import upload_file, ensure_bucket_exists, get_s3_client
from config.llm import compare_screenshots
from config import S3_BUCKET_NAME

logger = logging.getLogger(__name__)


async def async_run_every_minute(tracked_websites: list[TrackedWebsite]) -> None:
    """Async implementation with concurrent screenshot processing."""

    await sync_to_async(ensure_bucket_exists)()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        tasks: list[asyncio.Task[tuple[ImageHash, bytes]]] = []
        for tracked_website in tracked_websites:
            task: asyncio.Task[tuple[ImageHash, bytes]] = asyncio.create_task(
                async_get_screenshot_perceptual_hash(browser, tracked_website.url)
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        await browser.close()

    for i, tracked_website in enumerate(tracked_websites):
        perpetual_hash, screenshot_bytes = results[i]

        latest_screenshot = await sync_to_async(tracked_website.get_latest_screenshot)()
        perpetual_hash_str = str(perpetual_hash)

        if latest_screenshot is None or latest_screenshot.perceptual_hash != perpetual_hash_str:
            previous_hash = latest_screenshot.perceptual_hash if latest_screenshot else 'None'
            logger.info(
                f'Changes detected for {tracked_website.url} | '
                f'Previous Hash: {previous_hash} | Current Hash: {perpetual_hash_str}'
            )

            timestamp = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
            s3_key = f'screenshots/{tracked_website.id}/{timestamp}.png'

            await sync_to_async(upload_file)(screenshot_bytes, s3_key, content_type='image/png')

            change_summary = None
            if latest_screenshot is not None and latest_screenshot.s3_key:
                try:
                    s3_client = await sync_to_async(get_s3_client)()
                    previous_screenshot_bytes = await sync_to_async(
                        lambda: s3_client.get_object(
                            Bucket=S3_BUCKET_NAME, Key=latest_screenshot.s3_key
                        )['Body'].read()
                    )()

                    change_summary = await sync_to_async(compare_screenshots)(
                        previous_screenshot_bytes, screenshot_bytes, tracked_website.url
                    )
                except Exception as e:
                    logger.error(
                        f'Failed to generate change summary for {tracked_website.url}: {e}'
                    )

            await sync_to_async(WebsiteScreenshot.objects.create)(
                tracked_website=tracked_website,
                perceptual_hash=perpetual_hash_str,
                s3_key=s3_key,
                change_summary=change_summary,
            )
        else:
            logger.info(
                f'No changes detected for {tracked_website.url} | Hash: {perpetual_hash_str}'
            )


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
