from base.models import User
import pytest
from base.api.tests.conftest import DefaultTestValues

path = '/signup'
method = 'POST'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'username',
    [
        'validuser',
        'abcdef',
        'user123',
        'user@example',
        'user.name',
        'user+tag',
        'user-name',
        'user_name',
        'a' * 18,
    ],
)
def test_signup_username_valid(auth_client, username):
    """
    Test valid username formats are accepted for signup
    """
    json_body = {'username': username, 'password': DefaultTestValues.password}
    response = auth_client.request(method=method, path=path, json=json_body)

    assert response.status_code == 201
    assert response.json() == {'message': 'User created successfully'}
    assert User.objects.filter(username=username).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'username,expected_error_fragment',
    [
        ('', 'This field cannot be blank'),
        ('a' * 5, 'Ensure this value has at least 6 characters'),
        ('a' * 19, 'Ensure this value has at most 18 characters'),
    ],
)
def test_signup_username_length(auth_client, username, expected_error_fragment):
    """
    Test that usernames outside the 6-18 character range are rejected
    """
    json_body = {'username': username, 'password': DefaultTestValues.password}
    response = auth_client.request(method=method, path=path, json=json_body)

    assert response.status_code == 400
    assert expected_error_fragment in str(response.json()['detail'])


@pytest.mark.django_db
@pytest.mark.parametrize(
    'username',
    [
        'user name',
        'user#hash',
        'user$dollar',
        'user!exclaim',
        ' validuser',
        'validuser ',
        ' validuser ',
    ],
)
def test_signup_username_invalid_characters(auth_client, username):
    """
    Test that usernames with invalid characters or whitespace are rejected
    """
    json_body = {'username': username, 'password': DefaultTestValues.password}
    response = auth_client.request(method=method, path=path, json=json_body)
    invalid_chars_msg = (
        'Enter a valid username. This value may contain only letters, '
        'numbers, and @/./+/-/_ characters.'
    )

    assert response.status_code == 400
    assert invalid_chars_msg in str(response.json()['detail'])


@pytest.mark.django_db
def test_signup_username_case_sensitivity(auth_client):
    """
    Test that usernames are case-sensitive
    """
    json_body_1 = {'username': 'TestUser', 'password': DefaultTestValues.password}
    response_1 = auth_client.request(method=method, path=path, json=json_body_1)
    assert response_1.status_code == 201

    json_body_2 = {'username': 'testuser', 'password': DefaultTestValues.password}
    response_2 = auth_client.request(method=method, path=path, json=json_body_2)
    assert response_2.status_code == 201

    assert User.objects.filter(username='TestUser').exists()
    assert User.objects.filter(username='testuser').exists()
    assert User.objects.count() == 2


@pytest.mark.django_db
def test_signup_username_duplicate(auth_client, get_user):  # noqa: ARG001
    """
    Test that duplicate usernames are rejected
    """
    json_body = {'username': DefaultTestValues.username, 'password': DefaultTestValues.password}
    response = auth_client.request(method=method, path=path, json=json_body)

    assert response.status_code == 400
    assert 'A user with that username already exists.' in str(response.json()['detail'])


@pytest.mark.django_db
@pytest.mark.parametrize(
    'password',
    [
        'ValidPass123',
        'P@ssw0rd!',
        'a' * 128,
        'パスワード123',
        'test pass 123',
        'MyP@ssw0rd',
        '!@#$%^&*()',
    ],
)
def test_signup_password_valid(auth_client, password):
    """
    Test valid password formats are accepted for signup
    """
    json_body = {'username': DefaultTestValues.username, 'password': password}
    response = auth_client.request(method=method, path=path, json=json_body)

    assert response.status_code == 201
    assert response.json() == {'message': 'User created successfully'}


@pytest.mark.django_db
def test_signup_password_hashed(auth_client):
    """
    Test that passwords are stored hashed and not in plaintext
    """
    json_body = {'username': DefaultTestValues.username, 'password': DefaultTestValues.password}
    response = auth_client.request(method=method, path=path, json=json_body)
    assert response.status_code == 201

    user = User.objects.get(username=DefaultTestValues.username)
    assert user.check_password(DefaultTestValues.password)
    assert user.password != DefaultTestValues.password
    assert user.password.startswith('pbkdf2_sha256$')


@pytest.mark.django_db
def test_signup_user_logged_in(auth_client):
    """
    Test that user is automatically logged in after successful signup
    """
    json_body = {'username': DefaultTestValues.username, 'password': DefaultTestValues.password}
    response = auth_client.request(method=method, path=path, json=json_body)
    assert response.status_code == 201

    user = User.objects.get(username=DefaultTestValues.username)
    assert auth_client.session['_auth_user_id'] == str(user.pk)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'password,expected_errors',
    [
        ('', ['This password is too short. It must contain at least 8 characters.']),
        ('   ', ['This password is too short. It must contain at least 8 characters.']),
        ('short', ['This password is too short. It must contain at least 8 characters.']),
        (
            '1234567',
            [
                'This password is too short. It must contain at least 8 characters.',
                'This password is too common.',
                'This password is entirely numeric.',
            ],
        ),
        ('password', ['This password is too common.']),
        ('12345678', ['This password is too common.', 'This password is entirely numeric.']),
        ('qwerty123', ['This password is too common.']),
        ('87654321', ['This password is too common.', 'This password is entirely numeric.']),
        ('11111111', ['This password is too common.', 'This password is entirely numeric.']),
        (DefaultTestValues.username, ['The password is too similar to the username.']),
    ],
)
def test_signup_password_invalid(auth_client, password, expected_errors):
    """
    Test invalid password formats are rejected for signup
    """
    json_body = {'username': DefaultTestValues.username, 'password': password}
    response = auth_client.request(method=method, path=path, json=json_body)

    assert response.status_code == 400
    assert response.json()['detail'] == expected_errors
