from ninja.testing import TestClient
from base.api.favicon_ico import router_favicon
import pytest

client = TestClient(router_favicon)


@pytest.mark.django_db
def test_favicon_redirect():
    response = client.get('/favicon.ico')
    assert response.status_code == 301
    assert response.url == '/static/favicon.svg'
