from ninja.testing import TestClient
from . import router_track

client = TestClient(router_track)

path = '/track'
method = 'POST'


def test_track_happy_path():
    json_body = {'url': 'http://example.com'}

    response = client.request(method=method, path=path, json=json_body)
    assert response.status_code == 201
    assert response.json() == {
        'message': 'URL tracked successfully',
        'url': 'http://example.com/',
    }


def test_track_invalid_url():
    json_body = {'url': 'invalid-url'}

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
