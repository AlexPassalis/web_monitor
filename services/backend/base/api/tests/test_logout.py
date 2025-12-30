import pytest

from conftest import TestValues

path = '/logout'
method = 'POST'


@pytest.mark.django_db
def test_logout_when_logged_in(auth_client, get_user):
    """
    Test successful logout when user is logged in
    """
    user = get_user
    login_body = {'username': TestValues.username, 'password': TestValues.password}
    auth_client.request(method='POST', path='/login', json=login_body)

    assert auth_client.session.get('_auth_user_id') == str(user.pk)

    response = auth_client.request(method=method, path=path)

    assert response.status_code == 200
    assert response.json() == {'message': 'Logout successful'}
    assert auth_client.session.get('_auth_user_id') is None


@pytest.mark.django_db
def test_logout_when_not_logged_in(auth_client):
    """
    Test logout when user is not logged in
    """
    assert auth_client.session.get('_auth_user_id') is None

    response = auth_client.request(method=method, path=path)

    assert response.status_code == 200
    assert response.json() == {'message': 'Logout successful'}
    assert auth_client.session.get('_auth_user_id') is None
