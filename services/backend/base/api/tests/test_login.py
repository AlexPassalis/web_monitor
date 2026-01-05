import pytest

from base.models import User
from conftest import TestValues

path = '/login'
method = 'POST'


@pytest.mark.django_db
def test_login_success(auth_client, get_user):
    """
    Test successful login with valid credentials
    """
    user = get_user
    json_body = {'username': TestValues.username, 'password': TestValues.password}
    response = auth_client.request(method=method, path=path, json=json_body)

    assert response.status_code == 200
    assert response.json() == {'message': 'Login successful'}
    assert auth_client.session['_auth_user_id'] == str(user.pk)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'username,password',
    [
        (TestValues.username, 'WrongPass123!'),
        (TestValues.username.upper(), TestValues.password),
        (f' {TestValues.username} ', TestValues.password),
        ('', TestValues.password),
        (TestValues.username, ''),
        ('', ''),
        (TestValues.username, '     '),
        (TestValues.username, f' {TestValues.password} '),
    ],
)
def test_login_invalid_credentials(auth_client, get_user, username, password):
    """
    Test login failures with invalid credentials
    """
    json_body = {'username': username, 'password': password}
    response = auth_client.request(method=method, path=path, json=json_body)

    assert response.status_code == 401
    assert response.json() == {'detail': ['Invalid username or password']}


@pytest.mark.django_db
@pytest.mark.parametrize(
    'username,password',
    [
        (TestValues.username, None),
        (None, TestValues.password),
        (None, None),
    ],
)
def test_login_missing_fields(auth_client, get_user, username, password):
    """
    Test login failures with missing required fields
    """
    json_body = {}
    if username is not None:
        json_body['username'] = username
    if password is not None:
        json_body['password'] = password

    response = auth_client.request(method=method, path=path, json=json_body)

    assert response.status_code == 422


@pytest.mark.django_db
def test_login_non_existent_user(auth_client):
    """
    Test that login fails for non-existent user
    """
    json_body = {'username': TestValues.username, 'password': TestValues.password}
    response = auth_client.request(method=method, path=path, json=json_body)

    assert response.status_code == 401
    assert response.json()['detail'] == ['Invalid username or password']


@pytest.mark.django_db
def test_login_user_already_logged_in(auth_client, get_user):
    """
    Test that user can login again when already logged in
    """
    user = get_user
    json_body = {'username': TestValues.username, 'password': TestValues.password}

    response_1 = auth_client.request(method=method, path=path, json=json_body)
    assert response_1.status_code == 200

    response_2 = auth_client.request(method=method, path=path, json=json_body)
    assert response_2.status_code == 200
    assert response_2.json() == {'message': 'Login successful'}
    assert auth_client.session['_auth_user_id'] == str(user.pk)


@pytest.mark.django_db
def test_login_inactive_user(auth_client):
    """
    Test that inactive users cannot login
    """
    user = User.objects.create_user(
        username=TestValues.username,
        password=TestValues.password,
    )
    user.is_active = False
    user.save()

    json_body = {'username': TestValues.username, 'password': TestValues.password}
    response = auth_client.request(method=method, path=path, json=json_body)

    assert response.status_code == 401
    assert response.json()['detail'] == ['Invalid username or password']
