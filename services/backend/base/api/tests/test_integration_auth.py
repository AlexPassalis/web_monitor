from unittest.mock import patch

import pytest
from django.test import Client

from base.models import User
from conftest import TestValues


@pytest.mark.django_db
def test_complete_user_journey(auth_client):
    """
    Test complete user journey: Signup → Logout → Login
    """
    signup_response = auth_client.request(
        method='POST',
        path='/signup',
        json={'username': TestValues.username, 'password': TestValues.password},
    )
    assert signup_response.status_code == 201
    assert signup_response.json() == {'message': 'User created successfully'}
    user = User.objects.get(username=TestValues.username)
    assert auth_client.session['_auth_user_id'] == str(user.pk)

    logout_response = auth_client.request(method='POST', path='/logout')
    assert logout_response.status_code == 200
    assert logout_response.json() == {'message': 'Logout successful'}
    assert auth_client.session.get('_auth_user_id') is None

    login_response = auth_client.request(
        method='POST',
        path='/login',
        json={'username': TestValues.username, 'password': TestValues.password},
    )
    assert login_response.status_code == 200
    assert login_response.json() == {'message': 'Login successful'}
    assert auth_client.session['_auth_user_id'] == str(user.pk)


@pytest.mark.django_db
@patch('base.tasks.tasks.save_initial_screenshot.apply_async')
def test_session_persistence_across_requests(mock_task, get_user):
    """
    Test that session persists across multiple authenticated requests
    """
    user = get_user
    django_client = Client()

    login_response = django_client.post(
        '/api/login',
        data={'username': TestValues.username, 'password': TestValues.password},
        content_type='application/json',
    )
    assert login_response.status_code == 200
    assert django_client.session['_auth_user_id'] == str(user.pk)

    webpage_response_1 = django_client.post(
        '/api/webpage',
        data={'url': 'http://example1.com', 'interval': TestValues.interval},
        content_type='application/json',
    )
    assert webpage_response_1.status_code == 201
    assert django_client.session['_auth_user_id'] == str(user.pk)

    webpage_response_2 = django_client.post(
        '/api/webpage',
        data={'url': 'http://example2.com', 'interval': TestValues.interval},
        content_type='application/json',
    )
    assert webpage_response_2.status_code == 201
    assert django_client.session['_auth_user_id'] == str(user.pk)

    webpage_response_3 = django_client.post(
        '/api/webpage',
        data={'url': 'http://example3.com', 'interval': TestValues.interval},
        content_type='application/json',
    )
    assert webpage_response_3.status_code == 201
    assert django_client.session['_auth_user_id'] == str(user.pk)


@pytest.mark.django_db
def test_failed_login_does_not_corrupt_session(auth_client):
    """
    Test that failed login doesn't corrupt session for subsequent login
    """
    failed_login_response = auth_client.request(
        method='POST',
        path='/login',
        json={'username': TestValues.username, 'password': 'WrongPassword123!'},
    )
    assert failed_login_response.status_code == 401
    assert failed_login_response.json() == {'detail': ['Invalid username or password']}
    assert auth_client.session.get('_auth_user_id') is None

    User.objects.create_user(
        username=TestValues.username,
        password=TestValues.password,
    )

    success_login_response = auth_client.request(
        method='POST',
        path='/login',
        json={'username': TestValues.username, 'password': TestValues.password},
    )
    assert success_login_response.status_code == 200
    assert success_login_response.json() == {'message': 'Login successful'}

    user = User.objects.get(username=TestValues.username)
    assert auth_client.session['_auth_user_id'] == str(user.pk)


@pytest.mark.django_db
@patch('base.tasks.tasks.save_initial_screenshot.apply_async')
def test_user_data_isolation(_mock_task):
    """
    Test that authenticated users can only access their own data
    """
    django_client = Client()

    user_a = User.objects.create_user(username='usera1', password=TestValues.password)
    user_b = User.objects.create_user(username='userb1', password=TestValues.password)

    django_client.post(
        '/api/login',
        data={'username': 'usera1', 'password': TestValues.password},
        content_type='application/json',
    )
    assert django_client.session['_auth_user_id'] == str(user_a.pk)

    webpage_response_a = django_client.post(
        '/api/webpage',
        data={'url': 'http://user-a-site.com', 'interval': 'minute'},
        content_type='application/json',
    )
    assert webpage_response_a.status_code == 201
    webpage_a_id = webpage_response_a.json()['id']

    django_client.post('/api/logout')

    django_client.post(
        '/api/login',
        data={'username': 'userb1', 'password': TestValues.password},
        content_type='application/json',
    )
    assert django_client.session['_auth_user_id'] == str(user_b.pk)

    webpage_response_b = django_client.post(
        '/api/webpage',
        data={'url': 'http://user-b-site.com', 'interval': 'hour'},
        content_type='application/json',
    )
    assert webpage_response_b.status_code == 201

    get_response = django_client.get('/api/webpage')
    assert get_response.status_code == 200
    webpages = get_response.json()
    assert len(webpages) == 1
    assert webpages[0]['url'] == 'http://user-b-site.com/'

    delete_response = django_client.delete(
        '/api/webpage',
        data={'id': webpage_a_id},
        content_type='application/json',
    )
    assert delete_response.status_code == 404
    assert delete_response.json()['detail'][0]['msg'] == 'You are not monitoring this webpage'


@pytest.mark.django_db
@patch('base.tasks.tasks.save_initial_screenshot.apply_async')
def test_protected_endpoints_inaccessible_after_logout(_mock_task, get_user):
    """
    Test that logout fully terminates session access to protected endpoints
    """
    user = get_user
    django_client = Client()

    django_client.post(
        '/api/login',
        data={'username': TestValues.username, 'password': TestValues.password},
        content_type='application/json',
    )
    assert django_client.session['_auth_user_id'] == str(user.pk)

    webpage_response = django_client.post(
        '/api/webpage',
        data={'url': 'http://example.com', 'interval': 'minute'},
        content_type='application/json',
    )
    assert webpage_response.status_code == 201

    get_response = django_client.get('/api/webpage')
    assert get_response.status_code == 200
    assert len(get_response.json()) == 1

    me_response = django_client.get('/api/me')
    assert me_response.status_code == 200
    assert me_response.json()['username'] == TestValues.username

    django_client.post('/api/logout')

    get_response_after = django_client.get('/api/webpage')
    assert get_response_after.status_code == 401
    assert get_response_after.json() == {'detail': 'Unauthorized'}

    me_response_after = django_client.get('/api/me')
    assert me_response_after.status_code == 401
    assert me_response_after.json() == {'detail': 'Unauthorized'}


@pytest.mark.django_db
def test_session_switch_between_users():
    """
    Test that logging out and logging in as a different user properly switches context
    """
    django_client = Client()

    user_a = User.objects.create_user(username='usera2', password=TestValues.password)
    user_b = User.objects.create_user(username='userb2', password=TestValues.password)

    django_client.post(
        '/api/login',
        data={'username': 'usera2', 'password': TestValues.password},
        content_type='application/json',
    )
    assert django_client.session['_auth_user_id'] == str(user_a.pk)

    me_response_a = django_client.get('/api/me')
    assert me_response_a.status_code == 200
    assert me_response_a.json() == {'id': user_a.id, 'username': 'usera2'}

    django_client.post('/api/logout')

    django_client.post(
        '/api/login',
        data={'username': 'userb2', 'password': TestValues.password},
        content_type='application/json',
    )
    assert django_client.session['_auth_user_id'] == str(user_b.pk)

    me_response_b = django_client.get('/api/me')
    assert me_response_b.status_code == 200
    assert me_response_b.json() == {'id': user_b.id, 'username': 'userb2'}

    webpage_response = django_client.get('/api/webpage')
    assert webpage_response.status_code == 200
    assert webpage_response.json() == []
