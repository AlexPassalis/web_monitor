from ninja.testing import TestClient
from . import track_router

client = TestClient(track_router)


def test_track_happy_path():
    response = client.post('/track', json={'url': 'http://example.com'})

    assert response.status_code == 201
    assert response.json() == {
        'message': 'URL tracked successfully',
        'url': 'http://example.com/',
    }


def test_track_invalid_url():
    response = client.post('/track', json={'url': 'not-a-valid-url'})

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
