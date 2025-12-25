from ninja.testing import TestClient
from base.api.add_webpage import router_add_webpage
from django.contrib.auth.models import User
import pytest

client = TestClient(router_add_webpage)

path = '/add_webpage'
method = 'POST'
default_url = 'http://example.com'
default_interval = 'minute'


@pytest.mark.django_db
def test_get_webpage_auth():
    """
    Test that unauthenticated users cannot access the endpoint
    """

    json_body = {'url': default_url, 'interval': default_interval}

    response = client.request(method=method, path=path, json=json_body)
    assert response.status_code == 401


@pytest.fixture
def get_authenticated_user(db):
    user = User.objects.create_user(username='testuser', password='testpass')
    return user


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url,status_code,expected_json',
    [
        (
            default_url,
            201,
            {'message': 'Webpage tracked successfully'},
        ),
        (
            'invalid-url',
            422,
            {
                'detail': [
                    {
                        'ctx': {'error': 'relative URL without a base'},
                        'loc': ['body', 'data', 'url'],
                        'msg': 'Input should be a valid URL, relative URL without a base',
                        'type': 'url_parsing',
                    },
                ],
            },
        ),
    ],
)
def test_get_webpage(get_authenticated_user, url, status_code, expected_json):
    json_body = {'url': url, 'interval': default_interval}

    response = client.request(method=method, path=path, json=json_body, user=get_authenticated_user)
    assert response.status_code == status_code
    assert response.json() == expected_json
