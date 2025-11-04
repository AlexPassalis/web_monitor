from ninja.testing import TestClient
from .favicon_ico import router
import pytest

client = TestClient(router)


@pytest.mark.django_db
def test_favicon_redirect():
    response = client.get('/favicon.ico')
    assert response.status_code == 301
    assert response.url == '/static/favicon.svg'
