from base.api.auth import router_auth
from base.models import User
import pytest
from base.api.tests.conftest import TestClientWithSessions, DefaultTestValues
from django.test import Client

auth_client = TestClientWithSessions(router_auth)


@pytest.mark.django_db
def test_complete_user_journey():
    """
    Test complete user journey: Signup → Logout → Login
    """
    signup_response = auth_client.request(
        method='POST',
        path='/signup',
        json={'username': DefaultTestValues.username, 'password': DefaultTestValues.password},
    )
    assert signup_response.status_code == 201
    assert signup_response.json() == {'message': 'User created successfully'}
    user = User.objects.get(username=DefaultTestValues.username)
    assert auth_client.session['_auth_user_id'] == str(user.pk)

    logout_response = auth_client.request(method='POST', path='/logout')
    assert logout_response.status_code == 200
    assert logout_response.json() == {'message': 'Logout successful'}
    assert auth_client.session.get('_auth_user_id') is None

    login_response = auth_client.request(
        method='POST',
        path='/login',
        json={'username': DefaultTestValues.username, 'password': DefaultTestValues.password},
    )
    assert login_response.status_code == 200
    assert login_response.json() == {'message': 'Login successful'}
    assert auth_client.session['_auth_user_id'] == str(user.pk)


@pytest.mark.django_db
def test_session_persistence_across_requests(get_user):
    """
    Test that session persists across multiple authenticated requests
    """
    user = get_user
    django_client = Client()

    login_response = django_client.post(
        '/api/login',
        data={'username': DefaultTestValues.username, 'password': DefaultTestValues.password},
        content_type='application/json',
    )
    assert login_response.status_code == 200
    assert django_client.session['_auth_user_id'] == str(user.pk)

    add_webpage_response_1 = django_client.post(
        '/api/add_webpage',
        data={'url': 'http://example1.com', 'interval': DefaultTestValues.interval},
        content_type='application/json',
    )
    assert add_webpage_response_1.status_code == 201
    assert django_client.session['_auth_user_id'] == str(user.pk)

    add_webpage_response_2 = django_client.post(
        '/api/add_webpage',
        data={'url': 'http://example2.com', 'interval': DefaultTestValues.interval},
        content_type='application/json',
    )
    assert add_webpage_response_2.status_code == 201
    assert django_client.session['_auth_user_id'] == str(user.pk)

    add_webpage_response_3 = django_client.post(
        '/api/add_webpage',
        data={'url': 'http://example3.com', 'interval': DefaultTestValues.interval},
        content_type='application/json',
    )
    assert add_webpage_response_3.status_code == 201
    assert django_client.session['_auth_user_id'] == str(user.pk)


@pytest.mark.django_db
def test_failed_login_does_not_corrupt_session():
    """
    Test that failed login doesn't corrupt session for subsequent login
    """
    auth_client.session.flush()

    failed_login_response = auth_client.request(
        method='POST',
        path='/login',
        json={'username': DefaultTestValues.username, 'password': 'WrongPassword123!'},
    )
    assert failed_login_response.status_code == 401
    assert failed_login_response.json() == {'detail': 'Invalid username or password'}
    assert auth_client.session.get('_auth_user_id') is None

    User.objects.create_user(
        username=DefaultTestValues.username,
        password=DefaultTestValues.password,
    )

    success_login_response = auth_client.request(
        method='POST',
        path='/login',
        json={'username': DefaultTestValues.username, 'password': DefaultTestValues.password},
    )
    assert success_login_response.status_code == 200
    assert success_login_response.json() == {'message': 'Login successful'}

    user = User.objects.get(username=DefaultTestValues.username)
    assert auth_client.session['_auth_user_id'] == str(user.pk)
