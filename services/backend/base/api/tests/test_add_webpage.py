from ninja.testing import TestClient
from base.api.add_webpage import router_add_webpage
from django.contrib.auth.models import User
import pytest

client = TestClient(router_add_webpage)

path = '/add_webpage'
method = 'POST'

default_interval = 'minute'


@pytest.fixture
def get_authenticated_user(db):
    user = User.objects.create_user(username='testuser', password='testpass')
    return user


@pytest.mark.django_db
def test_track_happy_path(get_authenticated_user):
    json_body = {'url': 'http://example.com', 'interval': default_interval}

    response = client.request(method=method, path=path, json=json_body, user=get_authenticated_user)
    assert response.status_code == 201
    assert response.json() == {
        'message': 'Webpage tracked successfully',
    }


@pytest.mark.django_db
def test_track_invalid_url(get_authenticated_user):
    json_body = {'url': 'invalid-url', 'interval': default_interval}

    response = client.request(method=method, path=path, json=json_body, user=get_authenticated_user)
    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {
                'ctx': {'error': 'relative URL without a base'},
                'loc': ['body', 'data', 'url'],
                'msg': 'Input should be a valid URL, relative URL without a base',
                'type': 'url_parsing',
            },
        ],
    }
