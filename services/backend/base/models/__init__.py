import asyncio
import io
import logging
from typing import NamedTuple

import celery
import django.core.files.base
import django.core.files.storage
import imagehash
import PIL.Image
import playwright.async_api
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models

from config.utils import get_browser

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with password and username validation
        """
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.full_clean(exclude=['password'])
        validate_password(password, user)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """
    User model
    """

    objects: UserManager = UserManager()  # type: ignore[misc]

    username = models.CharField(
        max_length=18,
        unique=True,
        validators=[
            UnicodeUsernameValidator(),
            MinLengthValidator(6),
            MaxLengthValidator(18),
        ],
        help_text='Required. 6-18 characters. Letters, digits and @/./+/-/_ only.',
        error_messages={
            'unique': 'A user with that username already exists.',
        },
    )


class Webpage(models.Model):
    """
    Represents a webpage that is being monitored for changes
    """

    id = models.AutoField(primary_key=True)

    url = models.URLField(
        max_length=2048,
        unique=True,
        help_text='The URL of the webpage being monitored',
    )

    users = models.ManyToManyField(  # type: ignore[var-annotated]
        settings.AUTH_USER_MODEL,
        through='WebpageMonitoring',
        related_name='monitored_webpages',
        help_text='Users monitoring this webpage',
    )

    def get_latest_screenshot(self) -> 'WebpageScreenshot | None':
        """
        Retrieves the most recent screenshot of the webpage
        """
        return self.screenshots.first()  # type: ignore[attr-defined]

    def get_screenshots_created_at(
        self,
        limit: int | None = None,
    ) -> list[str]:
        """
        Retrieves screenshot creation timestamps for the webpage,
        optionally limited to the most recent ones,
        formatted as 'YYYYMMDD_HHMMSS_microseconds'
        """
        created_at_datetime = self.screenshots.values_list('created_at', flat=True)[:limit]  # type: ignore[attr-defined]
        screenshots_created_at: list[str] = []
        for datetime in created_at_datetime:
            screenshots_created_at.append(datetime.strftime('%Y%m%d_%H%M%S_%f'))
        return screenshots_created_at


class WebpageMonitoring(models.Model):
    """
    Represents which users are monitoring which webpages at what interval
    """

    webpage = models.ForeignKey(
        Webpage,
        on_delete=models.CASCADE,
        related_name='monitorings',
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='webpage_monitorings',
    )

    interval = models.CharField(
        max_length=6,
        choices=[
            ('minute', 'minute'),
            ('hour', 'hour'),
            ('day', 'day'),
        ],
    )

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        id = self.webpage.id
        result = super().delete(*args, **kwargs)

        if not WebpageMonitoring.objects.filter(webpage=self.webpage).exists():
            self.cleanup_s3.apply_async(
                args=(id,),
                queue='low_priority',
            )

        return result

    @staticmethod
    @celery.shared_task
    def cleanup_s3(webpage_id: int) -> None:
        """
        Delete all screenshots from S3 for a webpage and remove the webpage
        """
        if WebpageMonitoring.objects.filter(webpage_id=webpage_id).exists():  # Race condition check
            return

        storage = django.core.files.storage.default_storage
        prefix = f'webpagescreenshots/{webpage_id}/'

        try:
            _, files = storage.listdir(prefix)
        except FileNotFoundError:
            files = []

        for file_name in files:
            file_path = f'{prefix}{file_name}'
            storage.delete(file_path)

        Webpage.objects.filter(id=webpage_id).delete()

    class Meta:
        constraints = [  # noqa: RUF012
            models.UniqueConstraint(
                fields=['webpage', 'user'],
                name='unique_webpage_per_user',
            ),
            models.CheckConstraint(
                condition=models.Q(interval__in=['minute', 'hour', 'day']),
                name='valid_interval',
            ),
        ]


class ScreenshotResult(NamedTuple):
    perceptual_hash: str
    screenshot: bytes


class WebpageScreenshot(models.Model):
    """
    Represents a screenshot of a webpage at a specific point in time
    """

    id = models.AutoField(primary_key=True)

    webpage = models.ForeignKey(
        Webpage,
        on_delete=models.CASCADE,
        related_name='screenshots',
        help_text='The webpage this screenshot belongs to',
    )

    perceptual_hash = models.CharField(
        max_length=64,
        help_text='The perceptual hash of the screenshot for comparison',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='The timestamp when the screenshot was created',
    )

    class Meta:
        ordering = ['-created_at']  # noqa: RUF012

    @staticmethod
    async def save_screenshot(webpage_id: int) -> None:
        """
        Take screenshot of webpage and save if changed
        """
        webpage = await asyncio.to_thread(Webpage.objects.get, id=webpage_id)

        result = await WebpageScreenshot.take_screenshot(url=webpage.url)
        if result is None:
            return

        latest_screenshot = await asyncio.to_thread(webpage.get_latest_screenshot)
        if latest_screenshot and latest_screenshot.perceptual_hash == result.perceptual_hash:
            return

        webpagescreenshot = await asyncio.to_thread(
            WebpageScreenshot.objects.create,
            webpage_id=webpage.id,
            perceptual_hash=result.perceptual_hash,
        )

        timestamp = webpagescreenshot.created_at.strftime('%Y%m%d_%H%M%S_%f')
        file_path = f'webpagescreenshots/{webpage.id}/{timestamp}.png'
        await asyncio.to_thread(
            WebpageScreenshot.upload_screenshot_to_s3,
            result.screenshot,
            file_path,
        )

        logger.info('New screenshot saved for webpage with url: %s', webpage.url)

    @staticmethod
    async def take_screenshot(url: str) -> ScreenshotResult | None:
        """
        Take screenshot of webpage and return perceptual hash + screenshot
        """
        browser = await get_browser()
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        try:
            response = await page.goto(url, wait_until='networkidle', timeout=10000)
            if response and not response.ok:
                logger.error(
                    'WebpageScreenshot.take_screenshot url:%s bad response: %s',
                    url,
                    response.status,
                )
                return None

            screenshot = await page.screenshot(
                full_page=True,
                animations='disabled',
                caret='hide',
            )

            image = PIL.Image.open(io.BytesIO(screenshot))
            perceptual_hash = imagehash.phash(image)

            return ScreenshotResult(str(perceptual_hash), screenshot)
        except playwright.async_api.TimeoutError as err:
            logger.error('WebpageScreenshot.take_screenshot url:%s timeout error: %s', url, err)
            return None
        except playwright.async_api.Error as err:
            logger.error('WebpageScreenshot.take_screenshot url:%s navigation error: %s', url, err)
            return None
        except Exception as err:
            logger.error('WebpageScreenshot.take_screenshot url:%s unexpected error: %s', url, err)
            return None
        finally:
            await page.close()
            await context.close()

    @staticmethod
    def upload_screenshot_to_s3(webpagescreenshot: bytes, file_path: str) -> None:
        """
        Upload screenshot of webpage to S3 bucket
        """
        django.core.files.storage.default_storage.save(
            name=file_path,
            content=django.core.files.base.ContentFile(content=webpagescreenshot),
        )
