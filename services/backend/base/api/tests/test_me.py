import pytest
from django.test import Client

from conftest import TestValues

client = Client()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'is_authenticated,expected_status',
    [
        (True, 200),
        (False, 401),
    ],
)
def test_get_me(get_user, is_authenticated, expected_status):
    """
    Test /me endpoint returns user info when authenticated and 401 when not
    """
    user = get_user if is_authenticated else None
    if is_authenticated:
        client.post(
            '/api/login',
            data={'username': TestValues.username, 'password': TestValues.password},
            content_type='application/json',
        )

    response = client.get('/api/me')

    assert response.status_code == expected_status

    if is_authenticated:
        assert user is not None
        assert response.json() == {'id': user.id, 'username': user.username}
    else:
        assert response.json() == {'detail': 'Unauthorized'}
