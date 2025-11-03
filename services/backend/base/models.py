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

    def get_latest_snapshot(self) -> 'WebsiteSnapshot | None':
        """
        Retrieves the most recent snapshot of the tracked website.
        """
        return self.snapshot.first()


class WebsiteSnapshot(models.Model):
    """
    Represents a snapshot of a tracked website at a specific point in time.
    """

    id = models.AutoField(primary_key=True)

    tracked_website = models.ForeignKey(
        TrackedWebsite,
        on_delete=models.CASCADE,
        related_name='snapshot',
        help_text='The tracked website this snapshot belongs to.',
    )

    html_content = models.TextField(
        help_text='The HTML content of the page at the time of the snapshot.',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='The timestamp when the snapshot was created.',
    )

    class Meta:
        ordering = ['-created_at']
