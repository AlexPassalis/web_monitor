from django.contrib.sessions.backends.db import SessionStore
from ninja.testing import TestClient
from django.contrib.messages.storage.fallback import FallbackStorage
from base.models import User
import pytest
from base.api.auth import router_auth


class DefaultTestValues:
    """
    Default values for tests
    """

    username = 'testuser'
    password = 'ValidPass123!'
    url = 'http://example.com'
    interval = 'minute'


@pytest.fixture
def get_user(db):
    user = User.objects.create_user(
        username=DefaultTestValues.username,
        password=DefaultTestValues.password,
    )
    return user


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
