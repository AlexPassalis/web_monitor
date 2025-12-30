from ninja.testing import TestClient
from base.api.add_webpage import router_add_webpage
import pytest
from base.api.tests.conftest import DefaultTestValues
from base.models import User
from base.models import Webpage
from unittest.mock import patch

client = TestClient(router_add_webpage)

path = '/add_webpage'
method = 'POST'


@pytest.mark.django_db
def test_get_webpage_unauthorized():
    """
    Test that unauthenticated users cannot access the endpoint
    """
    json_body = {'url': DefaultTestValues.url, 'interval': DefaultTestValues.interval}

    response = client.request(method=method, path=path, json=json_body)
    assert response.status_code == 401


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    [
        DefaultTestValues.url,
        'https://subdomain.example.com:8080/path/to/page?foo=bar&baz=qux#section',
        'http://example.com/' + 'a' * 2000,
    ],
)
def test_get_webpage_valid(get_user, url):
    """
    Test that valid URLs are accepted and tracked successfully
    """

    json_body = {'url': url, 'interval': DefaultTestValues.interval}

    response = client.request(method=method, path=path, json=json_body, user=get_user)
    assert response.status_code == 201
    assert response.json() == {'message': 'Webpage tracked successfully'}

    webpage = Webpage.objects.get(url=url)
    assert webpage.url == url
    assert get_user in webpage.minute.all()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'json_body,expected_json',
    [
        (
            {'url': 'invalid-url', 'interval': DefaultTestValues.interval},
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
            {'url': 'http://example.com/' + 'a' * 2030, 'interval': DefaultTestValues.interval},
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
        ({'url': DefaultTestValues.url}, None),
        ({}, None),
    ],
)
def test_get_webpage_invalid(get_user, json_body, expected_json):
    """
    Test that invalid URLs and missing required fields are rejected with validation errors
    """

    response = client.request(method=method, path=path, json=json_body, user=get_user)
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
def test_get_webpage_interval_validation(get_user, interval, status_code):
    """
    Test that all valid intervals are accepted and invalid ones are rejected
    """
    json_body = {'url': DefaultTestValues.url, 'interval': interval}

    response = client.request(method=method, path=path, json=json_body, user=get_user)
    assert response.status_code == status_code


@pytest.mark.django_db
def test_get_webpage_idempotent_same_interval(get_user):
    """
    Test that adding the same URL with the same interval twice is idempotent
    """
    json_body = {'url': DefaultTestValues.url, 'interval': 'minute'}

    response_1 = client.request(method=method, path=path, json=json_body, user=get_user)
    assert response_1.status_code == 201

    response_2 = client.request(method=method, path=path, json=json_body, user=get_user)
    assert response_2.status_code == 201

    webpage = Webpage.objects.get(url=DefaultTestValues.url)
    assert webpage.minute.count() == 1
    assert get_user in webpage.minute.all()


@pytest.mark.django_db
def test_get_webpage_same_user_different_intervals(get_user):
    """
    Test that a user can track the same URL with different intervals
    """
    json_body_minute = {'url': DefaultTestValues.url, 'interval': 'minute'}
    json_body_hour = {'url': DefaultTestValues.url, 'interval': 'hour'}
    json_body_day = {'url': DefaultTestValues.url, 'interval': 'day'}

    response_1 = client.request(method=method, path=path, json=json_body_minute, user=get_user)
    assert response_1.status_code == 201

    response_2 = client.request(method=method, path=path, json=json_body_hour, user=get_user)
    assert response_2.status_code == 201

    response_3 = client.request(method=method, path=path, json=json_body_day, user=get_user)
    assert response_3.status_code == 201

    webpage = Webpage.objects.get(url=DefaultTestValues.url)
    assert get_user in webpage.minute.all()
    assert get_user in webpage.hour.all()
    assert get_user in webpage.day.all()


@pytest.mark.django_db
def test_get_webpage_multiple_users_same_url(get_user):
    """
    Test that different users can track the same URL
    """
    user_2 = User.objects.create_user(username='testuser2', password='ValidPass123!')

    json_body = {'url': DefaultTestValues.url, 'interval': 'minute'}

    response_1 = client.request(method=method, path=path, json=json_body, user=get_user)
    assert response_1.status_code == 201

    response_2 = client.request(method=method, path=path, json=json_body, user=user_2)
    assert response_2.status_code == 201

    webpage = Webpage.objects.get(url=DefaultTestValues.url)
    assert webpage.minute.count() == 2
    assert get_user in webpage.minute.all()
    assert user_2 in webpage.minute.all()


@pytest.mark.django_db
def test_get_webpage_user_added_to_correct_interval_group(get_user):
    """
    Test that user is added to the correct ManyToMany interval field
    """
    json_body_minute = {'url': 'http://example1.com/', 'interval': 'minute'}
    json_body_hour = {'url': 'http://example2.com/', 'interval': 'hour'}
    json_body_day = {'url': 'http://example3.com/', 'interval': 'day'}

    client.request(method=method, path=path, json=json_body_minute, user=get_user)
    webpage_minute = Webpage.objects.get(url='http://example1.com/')
    assert get_user in webpage_minute.minute.all()
    assert get_user not in webpage_minute.hour.all()
    assert get_user not in webpage_minute.day.all()

    client.request(method=method, path=path, json=json_body_hour, user=get_user)
    webpage_hour = Webpage.objects.get(url='http://example2.com/')
    assert get_user not in webpage_hour.minute.all()
    assert get_user in webpage_hour.hour.all()
    assert get_user not in webpage_hour.day.all()

    client.request(method=method, path=path, json=json_body_day, user=get_user)
    webpage_day = Webpage.objects.get(url='http://example3.com/')
    assert get_user not in webpage_day.minute.all()
    assert get_user not in webpage_day.hour.all()
    assert get_user in webpage_day.day.all()


@pytest.mark.django_db
@patch('base.models.WebpageScreenshot.save_screenshot.apply_async')
def test_get_webpage_task_triggered_on_new_webpage(mock_task, get_user):
    """
    Test that save_screenshot task is triggered only when webpage is created
    """
    json_body = {'url': DefaultTestValues.url, 'interval': 'minute'}

    response = client.request(method=method, path=path, json=json_body, user=get_user)
    assert response.status_code == 201

    webpage = Webpage.objects.get(url=DefaultTestValues.url)
    mock_task.assert_called_once_with(
        args=(webpage.id, DefaultTestValues.url), queue='high_priority'
    )


@pytest.mark.django_db
@patch('base.models.WebpageScreenshot.save_screenshot.apply_async')
def test_get_webpage_task_not_triggered_on_existing_webpage(mock_task, get_user):
    """
    Test that task is not triggered when webpage already exists
    """
    user_2 = User.objects.create_user(username='testuser2', password='ValidPass123!')

    json_body = {'url': DefaultTestValues.url, 'interval': 'minute'}

    client.request(method=method, path=path, json=json_body, user=get_user)
    mock_task.assert_called_once()

    mock_task.reset_mock()

    client.request(method=method, path=path, json=json_body, user=user_2)
    mock_task.assert_not_called()
