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

    users = models.ManyToManyField(
        User,
        help_text='Users tracking this website.',
    )

    def get_latest(self):
        """
        Retrieves the most recent snapshot of the tracked website.
        """
        return self.snapshots.first()


class WebsiteSnapshot(models.Model):
    """
    Represents a snapshot of a tracked website at a specific point in time.
    """

    id = models.AutoField(primary_key=True)

    tracked_website = models.ForeignKey(
        TrackedWebsite,
        on_delete=models.CASCADE,
        related_name='snapshots',
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
