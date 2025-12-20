from django.db import models
from django.contrib.auth.models import User


class Webpage(models.Model):
    """
    Represents a webpage that is being tracked for changes.
    """

    id = models.AutoField(primary_key=True)

    url = models.URLField(
        max_length=2048,
        unique=True,
        help_text='The URL of the webpage being tracked.',
    )

    minute = models.ManyToManyField(
        User,
        related_name='tracked_webpage_min',
        blank=True,
        help_text='Users tracking this webpage every 1 minute.',
    )

    hour = models.ManyToManyField(
        User,
        related_name='tracked_webpage_hour',
        blank=True,
        help_text='Users tracking this webpage every 1 hour.',
    )

    day = models.ManyToManyField(
        User,
        related_name='tracked_webpage_day',
        blank=True,
        help_text='Users tracking this webpage every 1 day.',
    )

    def get_latest_screenshot(self) -> 'WebpageScreenshot | None':
        """
        Retrieves the most recent screenshot of the tracked webpage.
        """
        return self.screenshots.first()


class WebpageScreenshot(models.Model):
    """
    Represents a screenshot of a tracked webpage at a specific point in time.
    """

    id = models.AutoField(primary_key=True)

    tracked_webpage = models.ForeignKey(
        Webpage,
        on_delete=models.CASCADE,
        related_name='screenshots',
        help_text='The tracked webpage this screenshot belongs to.',
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

    change_summary = models.TextField(
        null=True,
        blank=True,
        help_text='AI-generated summary of changes detected in this screenshot.',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='The timestamp when the screenshot was created.',
    )

    class Meta:
        ordering = ['-created_at']
