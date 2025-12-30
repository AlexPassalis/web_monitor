import boto3
import pytest
from django.conf import settings
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.db import SessionStore
from ninja.testing import TestClient

from base.api.auth import router_auth
from base.models import User, Webpage


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
