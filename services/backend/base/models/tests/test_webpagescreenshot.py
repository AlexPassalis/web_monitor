from unittest.mock import AsyncMock, MagicMock, patch

import django.core.files.storage
import playwright.async_api
import pytest
from asgiref.sync import async_to_sync
from django.conf import settings

from base.models import WebpageScreenshot
from conftest import TestValues


@pytest.mark.django_db
def test_upload_screenshot_to_s3():
    """
    Test that upload_screenshot_to_s3 saves the image to S3
    """
    image_bytes = (settings.BASE_DIR / 'image_test.jpg').read_bytes()
    file_path = 'webpage/test/test_image.jpg'

    WebpageScreenshot.upload_screenshot_to_s3(image_bytes, file_path)

    assert django.core.files.storage.default_storage.exists(file_path)
    with django.core.files.storage.default_storage.open(file_path) as file:
        saved_content = file.read()
        assert saved_content == image_bytes

    django.core.files.storage.default_storage.delete(file_path)


@pytest.mark.django_db(transaction=True)
def test_take_screenshot():
    """
    Test that take_screenshot captures a webpage and returns hash and bytes
    """
    result = async_to_sync(WebpageScreenshot.take_screenshot)(url=TestValues.url)
    assert result is not None

    assert isinstance(result.perceptual_hash, str)
    assert isinstance(result.screenshot, bytes)


@pytest.mark.django_db(transaction=True)
def test_save_screenshot(get_webpage):
    """
    Test that save_screenshot creates a screenshot record and uploads to S3
    """
    async_to_sync(WebpageScreenshot.save_screenshot)(get_webpage.id)

    webpagescreenshot = WebpageScreenshot.objects.get(webpage=get_webpage)
    assert webpagescreenshot.perceptual_hash is not None

    files = django.core.files.storage.default_storage.listdir(f'webpage/{get_webpage.id}')[1]
    assert len(files) == 1

    file_path = f'webpage/{get_webpage.id}/{files[0]}'
    assert django.core.files.storage.default_storage.exists(file_path)

    for file in files:
        django.core.files.storage.default_storage.delete(f'webpage/{get_webpage.id}/{file}')


@pytest.mark.django_db(transaction=True)
@patch('base.models.get_browser')
def test_take_screenshot_404_response(mock_get_browser):
    """
    Test that take_screenshot returns None when page.goto returns 404
    """
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status = 404

    mock_page = AsyncMock()
    mock_page.goto.return_value = mock_response

    mock_context = AsyncMock()
    mock_context.new_page.return_value = mock_page

    mock_browser = AsyncMock()
    mock_browser.new_context.return_value = mock_context

    mock_get_browser.return_value = mock_browser

    result = async_to_sync(WebpageScreenshot.take_screenshot)(url=TestValues.url)

    assert result is None
    mock_page.goto.assert_called_once()
    mock_page.close.assert_called_once()
    mock_context.close.assert_called_once()


@pytest.mark.django_db(transaction=True)
@patch('base.models.get_browser')
def test_take_screenshot_500_response(mock_get_browser):
    """
    Test that take_screenshot returns None when page.goto returns 500
    """
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status = 500

    mock_page = AsyncMock()
    mock_page.goto.return_value = mock_response

    mock_context = AsyncMock()
    mock_context.new_page.return_value = mock_page

    mock_browser = AsyncMock()
    mock_browser.new_context.return_value = mock_context

    mock_get_browser.return_value = mock_browser

    result = async_to_sync(WebpageScreenshot.take_screenshot)(url=TestValues.url)

    assert result is None
    mock_page.goto.assert_called_once()
    mock_page.close.assert_called_once()
    mock_context.close.assert_called_once()


@pytest.mark.django_db(transaction=True)
@patch('base.models.get_browser')
def test_take_screenshot_timeout_error(mock_get_browser):
    """
    Test that take_screenshot returns None when page.goto times out
    """
    mock_page = AsyncMock()
    mock_page.goto.side_effect = playwright.async_api.TimeoutError('Timeout 10000ms exceeded')

    mock_context = AsyncMock()
    mock_context.new_page.return_value = mock_page

    mock_browser = AsyncMock()
    mock_browser.new_context.return_value = mock_context

    mock_get_browser.return_value = mock_browser

    result = async_to_sync(WebpageScreenshot.take_screenshot)(url=TestValues.url)

    assert result is None
    mock_page.goto.assert_called_once()
    mock_page.close.assert_called_once()
    mock_context.close.assert_called_once()


@pytest.mark.django_db(transaction=True)
@patch('base.models.get_browser')
def test_take_screenshot_navigation_error(mock_get_browser):
    """
    Test that take_screenshot returns None when page.goto raises navigation error
    """
    mock_page = AsyncMock()
    mock_page.goto.side_effect = playwright.async_api.Error('net::ERR_NAME_NOT_RESOLVED')

    mock_context = AsyncMock()
    mock_context.new_page.return_value = mock_page

    mock_browser = AsyncMock()
    mock_browser.new_context.return_value = mock_context

    mock_get_browser.return_value = mock_browser

    result = async_to_sync(WebpageScreenshot.take_screenshot)(url=TestValues.url)

    assert result is None
    mock_page.goto.assert_called_once()
    mock_page.close.assert_called_once()
    mock_context.close.assert_called_once()


@pytest.mark.django_db(transaction=True)
@patch('base.models.get_browser')
def test_take_screenshot_unexpected_error(mock_get_browser):
    """
    Test that take_screenshot returns None when unexpected error occurs
    """
    mock_page = AsyncMock()
    mock_page.goto.side_effect = Exception('Unexpected error occurred')

    mock_context = AsyncMock()
    mock_context.new_page.return_value = mock_page

    mock_browser = AsyncMock()
    mock_browser.new_context.return_value = mock_context

    mock_get_browser.return_value = mock_browser

    result = async_to_sync(WebpageScreenshot.take_screenshot)(url=TestValues.url)

    assert result is None
    mock_page.goto.assert_called_once()
    mock_page.close.assert_called_once()
    mock_context.close.assert_called_once()


@pytest.mark.django_db(transaction=True)
@patch('base.models.WebpageScreenshot.take_screenshot')
def test_save_screenshot_aborts_when_take_screenshot_fails(mock_take_screenshot, get_webpage):
    """
    Test that save_screenshot aborts early when take_screenshot returns None
    """
    mock_take_screenshot.return_value = None

    async_to_sync(WebpageScreenshot.save_screenshot)(get_webpage.id)

    assert not WebpageScreenshot.objects.filter(webpage=get_webpage).exists()


@pytest.mark.django_db(transaction=True)
@patch('base.models.WebpageScreenshot.take_screenshot')
@patch('base.models.WebpageScreenshot.upload_screenshot_to_s3')
def test_save_screenshot_cleanup_on_s3_upload_failure(
    mock_upload, mock_take_screenshot, get_webpage
):
    """
    Test that DB record is deleted if S3 upload fails
    """
    mock_take_screenshot.return_value = MagicMock(
        screenshot=b'fake_image_data', perceptual_hash='abc123'
    )
    mock_upload.side_effect = Exception('S3 upload failed')

    with pytest.raises(Exception, match='S3 upload failed'):
        async_to_sync(WebpageScreenshot.save_screenshot)(get_webpage.id)

    assert not WebpageScreenshot.objects.filter(webpage=get_webpage).exists()
