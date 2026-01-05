from unittest.mock import patch

import pytest
from django.test import Client

from base.models import User, Webpage
from conftest import TestValues


@pytest.mark.django_db
@patch('base.tasks.tasks.save_initial_screenshot.apply_async')
def test_webpage_crud_lifecycle(_mock_task, get_user):
    """
    Test complete create → read → filter → delete workflow in a single session
    """
    user = get_user
    django_client = Client()

    django_client.post(
        '/api/login',
        data={'username': TestValues.username, 'password': TestValues.password},
        content_type='application/json',
    )
    assert django_client.session['_auth_user_id'] == str(user.pk)

    response_1 = django_client.post(
        '/api/webpage',
        data={'url': 'http://site-1.com/', 'interval': 'minute'},
        content_type='application/json',
    )
    assert response_1.status_code == 201
    webpage_1_id = response_1.json()['id']

    response_2 = django_client.post(
        '/api/webpage',
        data={'url': 'http://site-2.com/', 'interval': 'hour'},
        content_type='application/json',
    )
    assert response_2.status_code == 201
    webpage_2_id = response_2.json()['id']

    response_3 = django_client.post(
        '/api/webpage',
        data={'url': 'http://site-3.com/', 'interval': 'day'},
        content_type='application/json',
    )
    assert response_3.status_code == 201

    get_all_response = django_client.get('/api/webpage')
    assert get_all_response.status_code == 200
    all_webpages = get_all_response.json()
    assert len(all_webpages) == 3

    get_minute_response = django_client.get('/api/webpage?interval=minute')
    assert get_minute_response.status_code == 200
    minute_webpages = get_minute_response.json()
    assert len(minute_webpages) == 1
    assert minute_webpages[0]['url'] == 'http://site-1.com/'
    assert minute_webpages[0]['id'] == webpage_1_id

    delete_response = django_client.delete(
        '/api/webpage',
        data={'id': webpage_2_id},
        content_type='application/json',
    )
    assert delete_response.status_code == 200
    assert delete_response.json()['message'] == 'Webpage monitoring removed successfully'

    get_remaining_response = django_client.get('/api/webpage')
    assert get_remaining_response.status_code == 200
    remaining_webpages = get_remaining_response.json()
    assert len(remaining_webpages) == 2
    remaining_urls = {wp['url'] for wp in remaining_webpages}
    assert remaining_urls == {'http://site-1.com/', 'http://site-3.com/'}


@pytest.mark.django_db
@patch('base.tasks.tasks.save_initial_screenshot.apply_async')
def test_webpage_interval_update(_mock_task, get_user):
    """
    Test that a user can update the monitoring interval for an existing webpage
    """
    user = get_user
    django_client = Client()

    django_client.post(
        '/api/login',
        data={'username': TestValues.username, 'password': TestValues.password},
        content_type='application/json',
    )
    assert django_client.session['_auth_user_id'] == str(user.pk)

    create_response = django_client.post(
        '/api/webpage',
        data={'url': 'http://interval-test.com/', 'interval': 'minute'},
        content_type='application/json',
    )
    assert create_response.status_code == 201
    assert create_response.json()['message'] == 'Webpage is now being monitored'

    get_response_1 = django_client.get('/api/webpage')
    assert get_response_1.status_code == 200
    webpages_1 = get_response_1.json()
    assert len(webpages_1) == 1
    assert webpages_1[0]['interval'] == 'minute'

    update_response = django_client.post(
        '/api/webpage',
        data={'url': 'http://interval-test.com/', 'interval': 'hour'},
        content_type='application/json',
    )
    assert update_response.status_code == 200
    assert update_response.json()['message'] == 'Monitoring interval updated'

    get_response_2 = django_client.get('/api/webpage')
    assert get_response_2.status_code == 200
    webpages_2 = get_response_2.json()
    assert len(webpages_2) == 1
    assert webpages_2[0]['interval'] == 'hour'

    same_interval_response = django_client.post(
        '/api/webpage',
        data={'url': 'http://interval-test.com/', 'interval': 'hour'},
        content_type='application/json',
    )
    assert same_interval_response.status_code == 200
    assert (
        same_interval_response.json()['message']
        == 'Already monitoring this webpage with the same interval'
    )


@pytest.mark.django_db
@patch('base.tasks.tasks.save_initial_screenshot.apply_async')
def test_multi_user_shared_webpage_cleanup(_mock_task):
    """
    Test that shared webpages persist when one user stops monitoring,
    but are cleaned up when all users stop
    """
    django_client = Client()

    user_a = User.objects.create_user(username='user_a_1', password=TestValues.password)
    user_b = User.objects.create_user(username='user_b_1', password=TestValues.password)

    django_client.post(
        '/api/login',
        data={'username': 'user_a_1', 'password': TestValues.password},
        content_type='application/json',
    )
    assert django_client.session['_auth_user_id'] == str(user_a.pk)

    create_response_a = django_client.post(
        '/api/webpage',
        data={'url': 'http://shared-site.com/', 'interval': 'minute'},
        content_type='application/json',
    )
    assert create_response_a.status_code == 201
    webpage_id = create_response_a.json()['id']

    django_client.post('/api/logout')

    django_client.post(
        '/api/login',
        data={'username': 'user_b_1', 'password': TestValues.password},
        content_type='application/json',
    )
    assert django_client.session['_auth_user_id'] == str(user_b.pk)

    create_response_b = django_client.post(
        '/api/webpage',
        data={'url': 'http://shared-site.com/', 'interval': 'hour'},
        content_type='application/json',
    )
    assert create_response_b.status_code == 201
    assert create_response_b.json()['id'] == webpage_id

    delete_response_b = django_client.delete(
        '/api/webpage',
        data={'id': webpage_id},
        content_type='application/json',
    )
    assert delete_response_b.status_code == 200

    assert Webpage.objects.filter(id=webpage_id).exists()

    django_client.post('/api/logout')

    django_client.post(
        '/api/login',
        data={'username': 'user_a_1', 'password': TestValues.password},
        content_type='application/json',
    )
    assert django_client.session['_auth_user_id'] == str(user_a.pk)

    get_response_a = django_client.get('/api/webpage')
    assert get_response_a.status_code == 200
    webpages_a = get_response_a.json()
    assert len(webpages_a) == 1
    assert webpages_a[0]['url'] == 'http://shared-site.com/'

    with patch('base.models.WebpageMonitoring.cleanup_s3.apply_async') as mock_cleanup:
        delete_response_a = django_client.delete(
            '/api/webpage',
            data={'id': webpage_id},
            content_type='application/json',
        )
        assert delete_response_a.status_code == 200
        mock_cleanup.assert_called_once_with(args=(webpage_id,), queue='low_priority')
