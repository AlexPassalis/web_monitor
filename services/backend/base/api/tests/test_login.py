from base.api.auth import router_auth
from base.models import User
import pytest
from base.api.tests.conftest import TestClientWithSessions, DefaultTestValues

client = TestClientWithSessions(router_auth)

path = '/login'
method = 'POST'


@pytest.mark.django_db
def test_login_success(get_user):
    """
    Test successful login with valid credentials
    """
    user = get_user
    json_body = {'username': DefaultTestValues.username, 'password': DefaultTestValues.password}
    response = client.request(method=method, path=path, json=json_body)

    assert response.status_code == 200
    assert response.json() == {'message': 'Login successful'}
    assert client.session['_auth_user_id'] == str(user.pk)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'username,password',
    [
        (DefaultTestValues.username, 'WrongPass123!'),
        (DefaultTestValues.username.upper(), DefaultTestValues.password),
        (f' {DefaultTestValues.username} ', DefaultTestValues.password),
        ('', DefaultTestValues.password),
        (DefaultTestValues.username, ''),
        ('', ''),
        (DefaultTestValues.username, '     '),
        (DefaultTestValues.username, f' {DefaultTestValues.password} '),
    ],
)
def test_login_invalid_credentials(get_user, username, password):  # noqa: ARG001
    """
    Test login failures with invalid credentials
    """
    json_body = {'username': username, 'password': password}
    response = client.request(method=method, path=path, json=json_body)

    assert response.status_code == 401
    assert response.json() == {'detail': 'Invalid username or password'}


@pytest.mark.django_db
@pytest.mark.parametrize(
    'username,password',
    [
        (DefaultTestValues.username, None),
        (None, DefaultTestValues.password),
        (None, None),
    ],
)
def test_login_missing_fields(get_user, username, password):  # noqa: ARG001
    """
    Test login failures with missing required fields
    """
    json_body = {}
    if username is not None:
        json_body['username'] = username
    if password is not None:
        json_body['password'] = password

    response = client.request(method=method, path=path, json=json_body)

    assert response.status_code == 422


@pytest.mark.django_db
def test_login_non_existent_user():
    """
    Test that login fails for non-existent user
    """
    json_body = {'username': DefaultTestValues.username, 'password': DefaultTestValues.password}
    response = client.request(method=method, path=path, json=json_body)

    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid username or password'


@pytest.mark.django_db
def test_login_user_already_logged_in(get_user):
    """
    Test that user can login again when already logged in
    """
    user = get_user
    json_body = {'username': DefaultTestValues.username, 'password': DefaultTestValues.password}

    response_1 = client.request(method=method, path=path, json=json_body)
    assert response_1.status_code == 200

    response_2 = client.request(method=method, path=path, json=json_body)
    assert response_2.status_code == 200
    assert response_2.json() == {'message': 'Login successful'}
    assert client.session['_auth_user_id'] == str(user.pk)


@pytest.mark.django_db
def test_login_inactive_user():
    """
    Test that inactive users cannot login
    """
    user = User.objects.create_user(
        username=DefaultTestValues.username,
        password=DefaultTestValues.password,
    )
    user.is_active = False
    user.save()

    json_body = {'username': DefaultTestValues.username, 'password': DefaultTestValues.password}
    response = client.request(method=method, path=path, json=json_body)

    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid username or password'
