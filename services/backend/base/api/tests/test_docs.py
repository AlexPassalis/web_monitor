import pytest
from django.test import Client

client = Client()


@pytest.mark.django_db
def test_docs():
    """
    Test that the OpenAPI documentation UI endpoint is accessible
    """
    response = client.get('/api/docs')

    assert response.status_code == 200
    assert 'text/html' in response.headers['Content-Type']
