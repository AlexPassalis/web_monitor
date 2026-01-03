from unittest.mock import patch

import django.core.files.storage
import pytest
from django.core.files.base import ContentFile

from base.models import Webpage, WebpageMonitoring


@pytest.mark.django_db
@patch('base.models.WebpageMonitoring.cleanup_s3.apply_async')
def test_webpagemonitoring_delete_triggers_cleanup_when_last_user(
    mock_cleanup, get_user, get_webpage
):
    """
    Test that deleting the last monitoring triggers S3 cleanup task
    """
    monitoring = WebpageMonitoring.objects.create(
        user=get_user, webpage=get_webpage, interval='minute'
    )

    monitoring.delete()

    mock_cleanup.assert_called_once_with(args=(get_webpage.id,), queue='low_priority')
    assert not WebpageMonitoring.objects.filter(webpage=get_webpage).exists()


@pytest.mark.django_db
@patch('base.models.WebpageMonitoring.cleanup_s3.apply_async')
def test_webpagemonitoring_delete_no_cleanup_when_other_users_exist(
    mock_cleanup, get_user, get_webpage, db
):
    """
    Test that deleting monitoring does not trigger cleanup when other users are monitoring
    """
    from base.models import User

    other_user = User.objects.create_user(username='otheruser', password='ValidPass123!')

    monitoring_1 = WebpageMonitoring.objects.create(
        user=get_user, webpage=get_webpage, interval='minute'
    )
    WebpageMonitoring.objects.create(user=other_user, webpage=get_webpage, interval='hour')

    monitoring_1.delete()

    mock_cleanup.assert_not_called()
    assert WebpageMonitoring.objects.filter(webpage=get_webpage).exists()


@pytest.mark.django_db
def test_cleanup_s3_deletes_files_and_webpage(get_webpage):
    """
    Test that cleanup_s3 deletes all screenshots and the webpage
    """
    storage = django.core.files.storage.default_storage
    prefix = f'webpage/{get_webpage.id}/'

    file_1_path = f'{prefix}screenshot1.png'
    file_2_path = f'{prefix}screenshot2.png'
    storage.save(file_1_path, ContentFile(b'test image 1'))
    storage.save(file_2_path, ContentFile(b'test image 2'))

    assert storage.exists(file_1_path)
    assert storage.exists(file_2_path)

    WebpageMonitoring.cleanup_s3(get_webpage.id)

    assert not storage.exists(file_1_path)
    assert not storage.exists(file_2_path)
    assert not Webpage.objects.filter(id=get_webpage.id).exists()


@pytest.mark.django_db
def test_cleanup_s3_handles_no_files(get_webpage):
    """
    Test that cleanup_s3 handles case when no files exist for the webpage
    """
    WebpageMonitoring.cleanup_s3(get_webpage.id)

    assert not Webpage.objects.filter(id=get_webpage.id).exists()


@pytest.mark.django_db
def test_cleanup_s3_race_condition_check(get_user, get_webpage):
    """
    Test that cleanup_s3 aborts if another monitoring exists (race condition)
    """
    storage = django.core.files.storage.default_storage
    prefix = f'webpage/{get_webpage.id}/'
    file_path = f'{prefix}screenshot.png'
    storage.save(file_path, ContentFile(b'test image'))

    WebpageMonitoring.objects.create(user=get_user, webpage=get_webpage, interval='minute')

    WebpageMonitoring.cleanup_s3(get_webpage.id)

    assert storage.exists(file_path)
    assert Webpage.objects.filter(id=get_webpage.id).exists()

    storage.delete(file_path)
