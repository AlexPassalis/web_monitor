import pytest
from base.api.tests.conftest import DefaultTestValues
from django.test import Client

path = '/csrf'
method = 'GET'


@pytest.mark.django_db
def test_get_csrf_token(auth_client):
    """
    Test getting CSRF token successfully
    """
    response = auth_client.request(method=method, path=path)

    assert response.status_code == 200
    assert 'csrfToken' in response.json()
    assert response.json()['csrfToken'] is not None
    assert isinstance(response.json()['csrfToken'], str)
    assert len(response.json()['csrfToken']) == 64


@pytest.mark.django_db
def test_csrf_tokens_different_between_requests(auth_client):
    """
    Test that CSRF tokens are regenerated on each request
    """
    response_1 = auth_client.request(method=method, path=path)
    token_1 = response_1.json()['csrfToken']
    assert response_1.status_code == 200

    response_2 = auth_client.request(method=method, path=path)
    token_2 = response_2.json()['csrfToken']
    assert response_2.status_code == 200

    assert token_1 != token_2


@pytest.mark.django_db
def test_csrf_protection_on_authenticated_endpoint(get_user):  # noqa: ARG001
    """
    Test CSRF protection on authenticated endpoints
    """
    csrf_client = Client(enforce_csrf_checks=True)

    csrf_client.post(
        '/api/login',
        data={'username': DefaultTestValues.username, 'password': DefaultTestValues.password},
        content_type='application/json',
    )

    response_without_token = csrf_client.post(
        '/api/add_webpage',
        data={'url': DefaultTestValues.url, 'interval': DefaultTestValues.interval},
        content_type='application/json',
    )
    assert response_without_token.status_code == 403
    assert response_without_token.json() == {'detail': 'CSRF check Failed'}

    csrf_response = csrf_client.get('/api/csrf')
    csrf_token = csrf_response.json()['csrfToken']

    response_with_token = csrf_client.post(
        '/api/add_webpage',
        data={'url': DefaultTestValues.url, 'interval': DefaultTestValues.interval},
        content_type='application/json',
        HTTP_X_CSRFTOKEN=csrf_token,
    )
    assert response_with_token.status_code == 201
    assert response_with_token.json() == {'message': 'Webpage tracked successfully'}
