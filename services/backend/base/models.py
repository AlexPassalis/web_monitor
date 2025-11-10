from django.db import models
from django.contrib.auth.models import User


class TrackedWebsite(models.Model):
    """
    Represents a website that is being tracked for changes.
    """

    id = models.AutoField(primary_key=True)

    url = models.URLField(
        max_length=2048,
        unique=True,
        help_text='The URL of the page being tracked.',
    )

    minute = models.ManyToManyField(
        User,
        related_name='tracked_website_min',
        blank=True,
        help_text='Users tracking this website every 1 minute.',
    )

    hour = models.ManyToManyField(
        User,
        related_name='tracked_website_hour',
        blank=True,
        help_text='Users tracking this website every 1 hour.',
    )

    day = models.ManyToManyField(
        User,
        related_name='tracked_website_day',
        blank=True,
        help_text='Users tracking this website every 1 day.',
    )

    def get_latest_screenshot(self) -> 'WebsiteScreenshot | None':
        """
        Retrieves the most recent screenshot of the tracked website.
        """
        return self.screenshot.first()


class WebsiteScreenshot(models.Model):
    """
    Represents a screenshot of a tracked website at a specific point in time.
    """

    id = models.AutoField(primary_key=True)

    tracked_website = models.ForeignKey(
        TrackedWebsite,
        on_delete=models.CASCADE,
        related_name='screenshot',
        help_text='The tracked website this screenshot belongs to.',
    )

    perceptual_hash = models.CharField(
        max_length=64,
        help_text='The perceptual hash of the screenshot for comparison.',
    )

    s3_key = models.CharField(
        max_length=512,
        default='',
        help_text='The S3 object key where the screenshot is stored.',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='The timestamp when the screenshot was created.',
    )

    class Meta:
        ordering = ['-created_at']
