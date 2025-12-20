from ninja.testing import TestClient
from ..health import router
import pytest

client = TestClient(router)

@pytest.mark.django_db
def test_health_check():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
