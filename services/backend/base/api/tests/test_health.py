import pytest
from ninja.testing import TestClient

from base.api.health import router_health

client = TestClient(router_health)


@pytest.mark.django_db
def test_health_check():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
