from unittest.mock import patch

import pytest
from ninja.testing import TestClient

from base.api.webpage import router_webpage
from base.models import User, Webpage, WebpageMonitoring
from conftest import TestValues

client = TestClient(router_webpage)

path = '/webpage'


@pytest.mark.django_db
def test_webpage_post_unauthorized():
    """
    Test that unauthenticated users cannot access the endpoint
    """
    json_body = {'url': TestValues.url, 'interval': TestValues.interval}

    response = client.request(method='POST', path=path, json=json_body)
    assert response.status_code == 401


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    [
        TestValues.url,
        'https://subdomain.example.com:8080/path/to/page?foo=bar&baz=qux#section',
        'http://example.com/' + 'a' * 2000,
    ],
)
@patch('base.tasks.tasks.save_initial_screenshot.apply_async')
def test_webpage_post_valid(mock_task, get_user, url):
    """
    Test that valid URLs are accepted and monitored successfully
    """
    json_body = {'url': url, 'interval': TestValues.interval}

    response = client.request(method='POST', path=path, json=json_body, user=get_user)
    assert response.status_code == 201

    response_data = response.json()
    assert response_data['message'] == 'Webpage is now being monitored'
    assert response_data['url'] == url
    assert response_data['interval'] == TestValues.interval
    assert 'id' in response_data

    webpage = Webpage.objects.get(url=url)
    assert webpage.url == url
    assert WebpageMonitoring.objects.filter(
        webpage=webpage, user=get_user, interval=TestValues.interval
    ).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'json_body,expected_json',
    [
        (
            {'url': 'invalid-url', 'interval': TestValues.interval},
            {
                'detail': [
                    {
                        'ctx': {'error': 'relative URL without a base'},
                        'loc': ['body', 'data', 'url'],
                        'msg': 'Input should be a valid URL, relative URL without a base',
                        'type': 'url_parsing',
                    },
                ],
            },
        ),
        (
            {'url': 'http://example.com/' + 'a' * 2030, 'interval': TestValues.interval},
            {
                'detail': [
                    {
                        'ctx': {'actual_length': 2049, 'field_type': 'Value', 'max_length': 2048},
                        'loc': ['body', 'data', 'url'],
                        'msg': 'Value should have at most 2048 items after validation, not 2049',
                        'type': 'too_long',
                    },
                ],
            },
        ),
        ({'interval': 'minute'}, None),
        ({'url': TestValues.url}, None),
        ({}, None),
    ],
)
def test_webpage_post_invalid(get_user, json_body, expected_json):
    """
    Test that invalid URLs and missing required fields are rejected with validation errors
    """
    response = client.request(method='POST', path=path, json=json_body, user=get_user)
    assert response.status_code == 422

    if expected_json is not None:
        assert response.json() == expected_json


@pytest.mark.django_db
@pytest.mark.parametrize(
    'interval,status_code',
    [
        ('minute', 201),
        ('hour', 201),
        ('day', 201),
        ('weekly', 422),
        ('monthly', 422),
    ],
)
@patch('base.tasks.tasks.save_initial_screenshot.apply_async')
def test_webpage_post_interval_validation(mock_task, get_user, interval, status_code):
    """
    Test that all valid intervals are accepted and invalid ones are rejected
    """
    json_body = {'url': TestValues.url, 'interval': interval}

    response = client.request(method='POST', path=path, json=json_body, user=get_user)
    assert response.status_code == status_code


@pytest.mark.django_db
@patch('base.tasks.tasks.save_initial_screenshot.apply_async')
def test_webpage_post_idempotent_same_interval(mock_task, get_user):
    """
    Test that adding the same URL with the same interval twice is idempotent
    """
    json_body = {'url': TestValues.url, 'interval': 'minute'}

    response_1 = client.request(method='POST', path=path, json=json_body, user=get_user)
    assert response_1.status_code == 201

    response_2 = client.request(method='POST', path=path, json=json_body, user=get_user)
    assert response_2.status_code == 200

    webpage = Webpage.objects.get(url=TestValues.url)
    assert WebpageMonitoring.objects.filter(webpage=webpage, user=get_user).count() == 1
    assert WebpageMonitoring.objects.filter(
        webpage=webpage, user=get_user, interval='minute'
    ).exists()


@pytest.mark.django_db
@patch('base.tasks.tasks.save_initial_screenshot.apply_async')
def test_webpage_post_same_user_different_intervals(mock_task, get_user):
    """
    Test that a user can update monitoring interval for the same URL
    """
    json_body_minute = {'url': TestValues.url, 'interval': 'minute'}
    json_body_hour = {'url': TestValues.url, 'interval': 'hour'}
    json_body_day = {'url': TestValues.url, 'interval': 'day'}

    response_1 = client.request(method='POST', path=path, json=json_body_minute, user=get_user)
    assert response_1.status_code == 201

    response_2 = client.request(method='POST', path=path, json=json_body_hour, user=get_user)
    assert response_2.status_code == 200

    response_3 = client.request(method='POST', path=path, json=json_body_day, user=get_user)
    assert response_3.status_code == 200

    webpage = Webpage.objects.get(url=TestValues.url)
    assert WebpageMonitoring.objects.filter(webpage=webpage, user=get_user).count() == 1
    assert WebpageMonitoring.objects.filter(webpage=webpage, user=get_user, interval='day').exists()


@pytest.mark.django_db
@patch('base.tasks.tasks.save_initial_screenshot.apply_async')
def test_webpage_post_multiple_users_same_url(mock_task, get_user):
    """
    Test that different users can monitor the same URL
    """
    user_2 = User.objects.create_user(username='testuser2', password='ValidPass123!')

    json_body = {'url': TestValues.url, 'interval': 'minute'}

    response_1 = client.request(method='POST', path=path, json=json_body, user=get_user)
    assert response_1.status_code == 201

    response_2 = client.request(method='POST', path=path, json=json_body, user=user_2)
    assert response_2.status_code == 201

    webpage = Webpage.objects.get(url=TestValues.url)
    assert WebpageMonitoring.objects.filter(webpage=webpage, interval='minute').count() == 2
    assert WebpageMonitoring.objects.filter(
        webpage=webpage, user=get_user, interval='minute'
    ).exists()
    assert WebpageMonitoring.objects.filter(
        webpage=webpage, user=user_2, interval='minute'
    ).exists()


@pytest.mark.django_db
@patch('base.tasks.tasks.save_initial_screenshot.apply_async')
def test_webpage_post_user_added_to_correct_interval_group(mock_task, get_user):
    """
    Test that user is added to the correct interval in WebpageMonitoring
    """
    json_body_minute = {'url': 'http://example1.com/', 'interval': 'minute'}
    json_body_hour = {'url': 'http://example2.com/', 'interval': 'hour'}
    json_body_day = {'url': 'http://example3.com/', 'interval': 'day'}

    client.request(method='POST', path=path, json=json_body_minute, user=get_user)
    webpage_minute = Webpage.objects.get(url='http://example1.com/')
    assert WebpageMonitoring.objects.filter(
        webpage=webpage_minute, user=get_user, interval='minute'
    ).exists()
    assert not WebpageMonitoring.objects.filter(
        webpage=webpage_minute, user=get_user, interval='hour'
    ).exists()
    assert not WebpageMonitoring.objects.filter(
        webpage=webpage_minute, user=get_user, interval='day'
    ).exists()

    client.request(method='POST', path=path, json=json_body_hour, user=get_user)
    webpage_hour = Webpage.objects.get(url='http://example2.com/')
    assert not WebpageMonitoring.objects.filter(
        webpage=webpage_hour, user=get_user, interval='minute'
    ).exists()
    assert WebpageMonitoring.objects.filter(
        webpage=webpage_hour, user=get_user, interval='hour'
    ).exists()
    assert not WebpageMonitoring.objects.filter(
        webpage=webpage_hour, user=get_user, interval='day'
    ).exists()

    client.request(method='POST', path=path, json=json_body_day, user=get_user)
    webpage_day = Webpage.objects.get(url='http://example3.com/')
    assert not WebpageMonitoring.objects.filter(
        webpage=webpage_day, user=get_user, interval='minute'
    ).exists()
    assert not WebpageMonitoring.objects.filter(
        webpage=webpage_day, user=get_user, interval='hour'
    ).exists()
    assert WebpageMonitoring.objects.filter(
        webpage=webpage_day, user=get_user, interval='day'
    ).exists()


@pytest.mark.django_db
@patch('base.tasks.tasks.save_initial_screenshot.apply_async')
def test_webpage_post_task_triggered_on_new_webpage(mock_task, get_user):
    """
    Test that save_screenshot task is triggered only when webpage is created
    """
    json_body = {'url': TestValues.url, 'interval': 'minute'}

    response = client.request(method='POST', path=path, json=json_body, user=get_user)
    assert response.status_code == 201

    webpage = Webpage.objects.get(url=TestValues.url)
    mock_task.assert_called_once_with(args=(webpage.id,), queue='high_priority')


@pytest.mark.django_db
@patch('base.tasks.tasks.save_initial_screenshot.apply_async')
def test_webpage_post_task_not_triggered_on_existing_webpage(mock_task, get_user):
    """
    Test that task is not triggered when webpage already exists
    """
    user_2 = User.objects.create_user(username='testuser2', password='ValidPass123!')

    json_body = {'url': TestValues.url, 'interval': 'minute'}

    client.request(method='POST', path=path, json=json_body, user=get_user)
    mock_task.assert_called_once()

    mock_task.reset_mock()

    client.request(method='POST', path=path, json=json_body, user=user_2)
    mock_task.assert_not_called()


@pytest.mark.django_db
def test_webpage_get_unauthorized():
    """
    Test that unauthenticated users cannot access the GET endpoint
    """
    response = client.request(method='GET', path=path)
    assert response.status_code == 401


@pytest.mark.django_db
@pytest.mark.parametrize(
    'interval',
    ['minute', 'hour', 'day', None],
)
def test_webpage_get_by_interval(get_user, interval):
    """
    Test that GET returns webpages for specific interval or all intervals when None
    """
    webpage_min = Webpage.objects.create(url='http://minute.com/')
    webpage_hour = Webpage.objects.create(url='http://hour.com/')
    webpage_day = Webpage.objects.create(url='http://day.com/')

    WebpageMonitoring.objects.create(webpage=webpage_min, user=get_user, interval='minute')
    WebpageMonitoring.objects.create(webpage=webpage_hour, user=get_user, interval='hour')
    WebpageMonitoring.objects.create(webpage=webpage_day, user=get_user, interval='day')

    query_path = f'{path}?interval={interval}' if interval is not None else path
    response = client.request(method='GET', path=query_path, user=get_user)
    assert response.status_code == 200

    json_response = response.json()
    assert isinstance(json_response, list)

    if interval == 'minute':
        assert len(json_response) == 1
        assert json_response[0]['url'] == 'http://minute.com/'
        assert json_response[0]['id'] == webpage_min.id
        assert json_response[0]['interval'] == 'minute'
        assert isinstance(json_response[0]['screenshots'], list)
    elif interval == 'hour':
        assert len(json_response) == 1
        assert json_response[0]['url'] == 'http://hour.com/'
        assert json_response[0]['id'] == webpage_hour.id
        assert json_response[0]['interval'] == 'hour'
        assert isinstance(json_response[0]['screenshots'], list)
    elif interval == 'day':
        assert len(json_response) == 1
        assert json_response[0]['url'] == 'http://day.com/'
        assert json_response[0]['id'] == webpage_day.id
        assert json_response[0]['interval'] == 'day'
        assert isinstance(json_response[0]['screenshots'], list)
    else:
        assert len(json_response) == 3
        urls = {item['url'] for item in json_response}
        assert urls == {'http://minute.com/', 'http://hour.com/', 'http://day.com/'}


@pytest.mark.django_db
def test_webpage_delete_unauthorized():
    """
    Test that unauthenticated users cannot delete webpage monitoring
    """
    json_body = {'id': 1}

    response = client.request(method='DELETE', path=path, json=json_body)
    assert response.status_code == 401


@pytest.mark.django_db
@patch('base.tasks.tasks.save_initial_screenshot.apply_async')
def test_webpage_delete_valid(mock_task, get_user):
    """
    Test successful deletion of webpage monitoring
    """
    json_body = {'url': TestValues.url, 'interval': TestValues.interval}
    response = client.request(method='POST', path=path, json=json_body, user=get_user)
    assert response.status_code == 201

    webpage_id = response.json()['id']

    delete_body = {'id': webpage_id}
    response = client.request(method='DELETE', path=path, json=delete_body, user=get_user)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data['message'] == 'Webpage monitoring removed successfully'
    assert response_data['id'] == webpage_id
    assert response_data['url'] == TestValues.url

    assert not WebpageMonitoring.objects.filter(webpage__id=webpage_id, user=get_user).exists()


@pytest.mark.django_db
def test_webpage_delete_not_monitoring(get_user):
    """
    Test that users cannot delete webpage monitoring they are not tracking
    """
    webpage = Webpage.objects.create(url='http://other.com/')

    delete_body = {'id': webpage.id}
    response = client.request(method='DELETE', path=path, json=delete_body, user=get_user)
    assert response.status_code == 404

    response_data = response.json()
    assert response_data['detail'][0]['msg'] == 'You are not monitoring this webpage'
