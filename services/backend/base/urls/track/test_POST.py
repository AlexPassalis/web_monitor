from ninja.testing import TestClient
from . import router

client = TestClient(router)


def test_track():
    response = client.post('/track', json={'url': 'http://example.com'})

    assert response.status_code == 201
    assert response.json() == {
        'message': 'URL tracked successfully',
        'url': 'http://example.com/',
    }
