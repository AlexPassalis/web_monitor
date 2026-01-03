import pytest

from conftest import TestValues

path = '/me'
method = 'GET'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'is_authenticated,expected_status',
    [
        (True, 200),
        (False, 401),
    ],
)
def test_get_me(auth_client, get_user, is_authenticated, expected_status):
    """
    Test /me endpoint returns user info when authenticated and 401 when not
    """
    user = get_user if is_authenticated else None

    if is_authenticated:
        login_body = {'username': TestValues.username, 'password': TestValues.password}
        auth_client.request(method='POST', path='/login', json=login_body)

    response = auth_client.request(method=method, path=path)

    assert response.status_code == expected_status

    if is_authenticated:
        assert user is not None
        response_data = response.json()
        assert response_data['id'] == user.id
        assert response_data['username'] == user.username
    else:
        assert 'detail' in response.json()
