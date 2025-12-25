from base.api.auth import router_auth
import pytest
from base.api.tests.conftest import TestClientWithSessions, DefaultTestValues

client = TestClientWithSessions(router_auth)

path = '/logout'
method = 'POST'


@pytest.mark.django_db
def test_logout_when_logged_in(get_user):
    """
    Test successful logout when user is logged in
    """
    user = get_user
    login_body = {'username': DefaultTestValues.username, 'password': DefaultTestValues.password}
    client.request(method='POST', path='/login', json=login_body)

    assert client.session.get('_auth_user_id') == str(user.pk)

    response = client.request(method=method, path=path)

    assert response.status_code == 200
    assert response.json() == {'message': 'Logout successful'}
    assert client.session.get('_auth_user_id') is None


@pytest.mark.django_db
def test_logout_when_not_logged_in():
    """
    Test logout when user is not logged in
    """
    assert client.session.get('_auth_user_id') is None

    response = client.request(method=method, path=path)

    assert response.status_code == 200
    assert response.json() == {'message': 'Logout successful'}
    assert client.session.get('_auth_user_id') is None
