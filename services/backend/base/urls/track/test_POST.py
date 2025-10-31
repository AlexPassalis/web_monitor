from ninja.testing import TestClient
from . import router_track
import pytest

client = TestClient(router_track)

path = '/track'
method = 'POST'

default_interval = 'minute'


@pytest.mark.django_db
def test_track_happy_path():
    json_body = {'url': 'http://example.com', 'interval': default_interval}

    response = client.request(method=method, path=path, json=json_body)
    assert response.status_code == 201
    assert response.json() == {
        'message': 'URL tracked successfully',
    }


@pytest.mark.django_db
def test_track_invalid_url():
    json_body = {'url': 'invalid-url', 'interval': default_interval}

    response = client.request(method=method, path=path, json=json_body)
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
