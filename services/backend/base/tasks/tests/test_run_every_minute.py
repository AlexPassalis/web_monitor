import logging

import django.core.files.storage
import pytest
from ninja.testing import TestClient

from base.api.webpage import router_webpage
from base.models import Webpage, WebpageMonitoring, WebpageScreenshot
from base.tasks.tasks_beat import run_every_minute
from conftest import TestValues

client = TestClient(router_webpage)


@pytest.mark.django_db(transaction=True)
def test_run_every_minute_no_change(get_user):
    """
    Test that run_every_minute does not create duplicate screenshots when page hasn't changed
    """
    json_body = {'url': TestValues.url, 'interval': 'minute'}

    response = client.request(method='POST', path='/webpage', json=json_body, user=get_user)
    assert response.status_code == 201

    webpage = Webpage.objects.get(url=TestValues.url)
    initial_screenshot = webpage.get_latest_screenshot()
    assert initial_screenshot is not None

    run_every_minute()

    latest_screenshot = webpage.get_latest_screenshot()
    assert latest_screenshot is not None
    assert latest_screenshot.id == initial_screenshot.id
    assert WebpageScreenshot.objects.filter(webpage=webpage).count() == 1

    screenshot_dir = f'webpagescreenshots/{webpage.id}'
    files = django.core.files.storage.default_storage.listdir(screenshot_dir)[1]
    file_path = f'{screenshot_dir}/{files[0]}'
    django.core.files.storage.default_storage.delete(file_path)


@pytest.mark.django_db(transaction=True)
def test_run_every_minute_creates_screenshot_when_missing(get_user, get_webpage):
    """
    Test that run_every_minute triggers screenshot creation for webpages without screenshots
    """
    WebpageMonitoring.objects.create(webpage=get_webpage, user=get_user, interval='minute')
    assert get_webpage.get_latest_screenshot() is None

    run_every_minute()

    screenshot = get_webpage.get_latest_screenshot()
    assert screenshot is not None
    assert screenshot.perceptual_hash is not None

    files = django.core.files.storage.default_storage.listdir(
        f'webpagescreenshots/{get_webpage.id}'
    )[1]
    assert len(files) == 1

    file_path = f'webpagescreenshots/{get_webpage.id}/{files[0]}'
    assert django.core.files.storage.default_storage.exists(file_path)

    django.core.files.storage.default_storage.delete(file_path)


@pytest.mark.django_db(transaction=True)
def test_run_every_minute_no_webpages_monitored(caplog):
    """
    Test that run_every_minute logs info message when no webpages are being monitored
    """
    assert WebpageMonitoring.objects.filter(interval='minute').count() == 0

    with caplog.at_level(logging.INFO):
        run_every_minute()

    assert 'There are no webpages being monitored every minute' in caplog.text
