from base.api.auth import router_auth
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
import pytest
from ninja.testing import TestClient
from django.contrib.messages.storage.fallback import FallbackStorage


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


client = TestClientWithSessions(router_auth)

path = '/signup'
method = 'POST'
default_password = 'testpass123'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'username',
    [
        'validuser',
        'a',
        'user123',
        'user@example',
        'user.name',
        'user+tag',
        'user-name',
        'user_name',
        'a' * 150,
    ],
)
def test_signup_username_valid(username):
    """
    Test valid username formats are accepted for signup
    """

    json_body = {'username': username, 'password': default_password}
    response = client.request(method=method, path=path, json=json_body)
    assert response.status_code == 201
    assert response.json() == {'message': 'User created successfully'}
    assert User.objects.filter(username=username).exists()


@pytest.mark.django_db
def test_signup_username_length():
    """
    Test that usernames exceeding 150 characters are rejected
    """

    json_body = {'username': 'a' * 151, 'password': default_password}
    response = client.request(method=method, path=path, json=json_body)

    assert response.status_code == 400
    assert 'Ensure this value has at most 150 characters' in str(response.json()['detail'])


@pytest.mark.django_db
@pytest.mark.parametrize(
    'username',
    [
        'user name',
        'user#hash',
        'user$dollar',
        'user!exclaim',
    ],
)
def test_signup_username_invalid_characters(username):
    """
    Test that usernames with invalid characters are rejected
    """

    json_body = {'username': username, 'password': default_password}
    response = client.request(method=method, path=path, json=json_body)
    invalid_chars_msg = (
        'Enter a valid username. This value may contain only letters, '
        'numbers, and @/./+/-/_ characters.'
    )

    assert response.status_code == 400
    assert invalid_chars_msg in str(response.json()['detail'])


@pytest.mark.django_db
def test_signup_username_case_sensitivity():
    """
    Test that usernames are case-sensitive
    """

    json_body_1 = {'username': 'TestUser', 'password': default_password}
    response_1 = client.request(method=method, path=path, json=json_body_1)
    assert response_1.status_code == 201

    json_body_2 = {'username': 'testuser', 'password': default_password}
    response_2 = client.request(method=method, path=path, json=json_body_2)
    assert response_2.status_code == 201

    assert User.objects.filter(username='TestUser').exists()
    assert User.objects.filter(username='testuser').exists()
    assert User.objects.count() == 2


@pytest.mark.django_db
def test_signup_username_duplicate():
    """
    Test that duplicate usernames are rejected
    """

    User.objects.create_user(username='existinguser', password='oldpass')

    json_body = {'username': 'existinguser', 'password': default_password}
    response = client.request(method=method, path=path, json=json_body)
    assert response.status_code == 400
    assert 'A user with that username already exists.' in str(response.json()['detail'])
