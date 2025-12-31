import pytest
from django.test import Client

client = Client()


@pytest.mark.django_db
def test_openapi_json():
    """
    Test that the OpenAPI JSON schema endpoint returns valid JSON
    """
    response = client.get('/api/openapi.json')

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'

    data = response.json()
    assert 'openapi' in data
    assert 'info' in data
    assert 'paths' in data

    assert data['info']['title'] == 'Backend API Service'
    assert data['info']['version'] == '0.0.1'
    assert data['info']['description'] == 'API for tracking webpage changes'
