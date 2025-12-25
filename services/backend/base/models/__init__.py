from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.conf import settings


class UserManager(BaseUserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with password and username validation
        """

        user = self.model(username=username, email=email, **extra_fields)
        user.full_clean(exclude=['password'])
        validate_password(password, user)
        return super()._create_user(username, email, password, **extra_fields)  # type: ignore[misc]


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
    Represents a webpage that is being tracked for changes
    """

    id = models.AutoField(primary_key=True)

    url = models.URLField(
        max_length=2048,
        unique=True,
        help_text='The URL of the webpage being tracked',
    )

    minute = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='tracked_webpage_min',
        blank=True,
        help_text='Users tracking this webpage every 1 minute',
    )

    hour = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='tracked_webpage_hour',
        blank=True,
        help_text='Users tracking this webpage every 1 hour',
    )

    day = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='tracked_webpage_day',
        blank=True,
        help_text='Users tracking this webpage every 1 day',
    )

    def get_latest_screenshot(self) -> 'WebpageScreenshot | None':
        """
        Retrieves the most recent screenshot of the tracked webpage
        """
        return self.screenshots.first()  # type: ignore[attr-defined]


class WebpageScreenshot(models.Model):
    """
    Represents a screenshot of a tracked webpage at a specific point in time
    """

    id = models.AutoField(primary_key=True)

    tracked_webpage = models.ForeignKey(
        Webpage,
        on_delete=models.CASCADE,
        related_name='screenshots',
        help_text='The tracked webpage this screenshot belongs to',
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
        ordering = ['-created_at']
