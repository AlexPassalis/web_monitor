from base.models import Webpage

import logging

from asgiref.sync import async_to_sync
from celery import shared_task


logger = logging.getLogger(__name__)


async def async_run_every_minute(tracked_webpages: list[Webpage]) -> None:
    """Async implementation with concurrent screenshot processing."""

    # async with async_playwright() as p:
    #     browser = await p.chromium.launch(headless=True)

    #     tasks: list[asyncio.Task[tuple[ImageHash, bytes]]] = []
    #     for tracked_webpage in tracked_webpages:
    #         task: asyncio.Task[tuple[ImageHash, bytes]] = asyncio.create_task(
    #             async_get_screenshot_perceptual_hash(browser, tracked_webpage.url)
    #         )
    #         tasks.append(task)

    #     results = await asyncio.gather(*tasks)

    #     await browser.close()

    # for i, tracked_webpage in enumerate(tracked_webpages):
    #     perpetual_hash, screenshot_bytes = results[i]

    #     latest_screenshot = await sync_to_async(tracked_webpage.get_latest_screenshot)()
    #     perpetual_hash_str = str(perpetual_hash)

    #     if latest_screenshot is None or latest_screenshot.perceptual_hash != perpetual_hash_str:
    #         previous_hash = latest_screenshot.perceptual_hash if latest_screenshot else 'None'
    #         logger.info(
    #             f'Changes detected for {tracked_webpage.url} | '
    #             f'Previous Hash: {previous_hash} | Current Hash: {perpetual_hash_str}'
    #         )

    #         timestamp = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
    #         s3_key = f'screenshots/{tracked_webpage.id}/{timestamp}.png'

    #         await sync_to_async(upload_file)(screenshot_bytes, s3_key, content_type='image/png')

    #         change_summary = None
    #         if latest_screenshot is not None and latest_screenshot.s3_key:
    #             try:
    #                 s3_client = await sync_to_async(get_s3_client)()
    #                 previous_screenshot_bytes = await sync_to_async(
    #                     lambda: s3_client.get_object(
    #                         Bucket=S3_BUCKET_NAME, Key=latest_screenshot.s3_key
    #                     )['Body'].read()
    #                 )()

    #                 change_summary = await sync_to_async(compare_screenshots)(
    #                     previous_screenshot_bytes, screenshot_bytes, tracked_webpage.url
    #                 )
    #             except Exception as e:
    #                 logger.error(
    #                     f'Failed to generate change summary for {tracked_webpage.url}: {e}'
    #                 )

    #         await sync_to_async(WebpageScreenshot.objects.create)(
    #             tracked_webpage=tracked_webpage,
    #             perceptual_hash=perpetual_hash_str,
    #             s3_key=s3_key,
    #             change_summary=change_summary,
    #         )
    #     else:
    #         logger.info(
    #             f'No changes detected for {tracked_webpage.url} | Hash: {perpetual_hash_str}'
    #         )


@shared_task
def run_every_minute() -> None:
    """Celery task that runs every minute."""

    tracked_webpages_qs = Webpage.objects.exclude(minute__isnull=True).distinct()
    if not tracked_webpages_qs.exists():
        logger.info('There are no webpages being tracked every minute.')
        return

    tracked_webpages = list(tracked_webpages_qs)
    async_to_sync(async_run_every_minute)(tracked_webpages)


#        latest_snapshot = tracked_webpage.get_latest_snapshot()
#        if latest_snapshot is None or latest_snapshot.html_content != html_content:
#            webpageSnapshot.objects.create(
#                tracked_webpage=tracked_webpage,
#                html_content=html_content,
#            )
#            logger.info(f'New snapshot created for {tracked_webpage.url}')
#        else:
#            logger.info(f'No changes detected for {tracked_webpage.url}')
