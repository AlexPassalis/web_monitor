import django.core.files.storage
import imagehash
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
    file_path = 'webpagescreenshots/test/test_image.jpg'

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
    perceptual_hash, webpagescreenshot = async_to_sync(WebpageScreenshot.take_screenshot)(
        url=TestValues.url
    )

    assert isinstance(perceptual_hash, imagehash.ImageHash)
    assert isinstance(webpagescreenshot, bytes)


@pytest.mark.django_db(transaction=True)
def test_save_screenshot(get_webpage):
    """
    Test that save_screenshot creates a screenshot record and uploads to S3
    """
    WebpageScreenshot.save_screenshot(get_webpage.id, TestValues.url)

    webpagescreenshot = WebpageScreenshot.objects.get(tracked_webpage=get_webpage)
    assert webpagescreenshot.perceptual_hash is not None

    files = django.core.files.storage.default_storage.listdir(
        f'webpagescreenshots/{get_webpage.id}'
    )[1]
    file_path = f'webpagescreenshots/{get_webpage.id}/{files[0]}'
    assert django.core.files.storage.default_storage.exists(file_path)
    django.core.files.storage.default_storage.delete(file_path)
