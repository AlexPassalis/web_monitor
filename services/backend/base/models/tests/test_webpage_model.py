from unittest.mock import MagicMock, patch

import pytest

from base.models import Webpage, WebpageMonitoring, WebpageScreenshot


@pytest.mark.django_db
def test_webpage_get_screenshots_created_at(get_webpage):
    """
    Test that get_screenshots_created_at returns formatted timestamp strings
    """
    screenshot_1 = WebpageScreenshot.objects.create(webpage=get_webpage, perceptual_hash='hash1')
    screenshot_2 = WebpageScreenshot.objects.create(webpage=get_webpage, perceptual_hash='hash2')

    timestamps = get_webpage.get_screenshots_created_at()

    assert len(timestamps) == 2
    assert timestamps[0] == screenshot_2.created_at.strftime('%Y%m%d_%H%M%S_%f')
    assert timestamps[1] == screenshot_1.created_at.strftime('%Y%m%d_%H%M%S_%f')


@pytest.mark.django_db
def test_webpage_get_screenshots_created_at_with_limit(get_webpage):
    """
    Test that get_screenshots_created_at respects the limit parameter
    """
    WebpageScreenshot.objects.create(webpage=get_webpage, perceptual_hash='hash1')
    WebpageScreenshot.objects.create(webpage=get_webpage, perceptual_hash='hash2')
    WebpageScreenshot.objects.create(webpage=get_webpage, perceptual_hash='hash3')

    timestamps = get_webpage.get_screenshots_created_at(limit=2)

    assert len(timestamps) == 2


@pytest.mark.django_db
def test_cleanup_s3_handles_missing_directory(get_webpage):
    """
    Test that cleanup_s3 handles FileNotFoundError when directory doesn't exist
    """
    mock_storage = MagicMock()
    mock_storage.listdir.side_effect = FileNotFoundError('Directory does not exist')

    with patch('django.core.files.storage.default_storage', mock_storage):
        WebpageMonitoring.cleanup_s3(get_webpage.id)

    assert not Webpage.objects.filter(id=get_webpage.id).exists()
