import io

import boto3
import pytest
from django.conf import settings
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.db import SessionStore
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from ninja.testing import TestClient
from PIL import Image

from base.api.auth import router_auth
from base.models import User, Webpage
from config.celery import app


class TestValues:
    username = 'testuser'
    password = 'ValidPass123!'
    url = 'http://example.com/'
    interval = 'minute'


@pytest.fixture
def get_user(db):
    user = User.objects.create_user(
        username=TestValues.username,
        password=TestValues.password,
    )
    return user


@pytest.fixture
def get_webpage(db):
    """
    Create a webpage with the default test URL
    """
    webpage = Webpage.objects.create(url=TestValues.url)
    return webpage


@pytest.fixture(scope='session', autouse=True)
def create_s3_bucket():
    """
    Create the S3 bucket before running tests
    """
    s3_client = boto3.client(
        's3',
        endpoint_url=settings.STORAGES['default']['OPTIONS']['endpoint_url'],
        aws_access_key_id=settings.STORAGES['default']['OPTIONS']['access_key'],
        aws_secret_access_key=settings.STORAGES['default']['OPTIONS']['secret_key'],
    )

    try:
        s3_client.create_bucket(Bucket=settings.STORAGES['default']['OPTIONS']['bucket_name'])
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        pass


@pytest.fixture(scope='session', autouse=True)
def setup_celery_eager_mode():
    """
    Force Celery to run in eager mode for all tests
    """
    app.conf.task_always_eager = True
    app.conf.task_eager_propagates = True


@pytest.fixture
def create_test_image():
    """
    Helper fixture to create test images with various modes
    """

    def _create_image(mode='RGB', size=(800, 600), color=(255, 0, 0)):
        """
        Create a test image and return as bytes
        """
        image = Image.new(mode, size, color)
        buffer = io.BytesIO()
        if mode in ('RGBA', 'LA'):
            image.save(buffer, format='PNG')
        else:
            image.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer.getvalue()

    return _create_image


@pytest.fixture
def save_test_image_to_storage(create_test_image):
    """
    Helper fixture to save test images to storage and clean up after
    """
    saved_paths = []

    def _save(path, mode='RGB', size=(800, 600), color=(255, 0, 0)):
        """
        Save a test image to storage and track for cleanup
        """
        image_bytes = create_test_image(mode=mode, size=size, color=color)
        default_storage.save(path, ContentFile(image_bytes))
        saved_paths.append(path)
        return path

    yield _save

    for path in saved_paths:
        if default_storage.exists(path):
            default_storage.delete(path)


@pytest.fixture
def reset_browser_state():
    """
    Reset browser global state before and after each test
    """
    from config import utils

    utils.browser_data.clear()
    utils.async_locks.clear()
    yield
    utils.browser_data.clear()
    utils.async_locks.clear()


@pytest.fixture
def auth_client():
    return TestClientWithSessions(router_auth)


# https://github.com/vitalik/django-ninja/issues/1321#issuecomment-2954236336
class TestClientWithSessions(TestClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = SessionStore()

    def _build_request(self, *args, **kwargs):
        mock = super()._build_request(*args, **kwargs)
        mock.session = self.session
        messages = FallbackStorage(mock)
        mock._messages = messages
        return mock
