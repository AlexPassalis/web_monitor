import io
from unittest.mock import MagicMock, Mock, patch

import pytest
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from ninja.testing import TestClient
from PIL import Image

from base.api.image import get_format_config, resize_image, router_image

client = TestClient(router_image)


@pytest.mark.django_db
def test_image_unauthorized():
    """
    Test that unauthenticated users cannot access images
    """
    response = client.get('/image/webpage/1/test.png')

    assert response.status_code == 401


@pytest.mark.django_db
def test_image_not_found(get_user):
    """
    Test that requesting a non-existent image returns 404
    """
    response = client.get('/image/webpage/999/nonexistent.png', user=get_user)

    assert response.status_code == 404


@pytest.mark.django_db
def test_image_basic_retrieval(get_user, get_webpage, save_test_image_to_storage):
    """
    Test basic image retrieval with default WebP format
    """
    path = save_test_image_to_storage(f'webpage/{get_webpage.id}/basic.png')

    response = client.get(f'/image/{path}', user=get_user)

    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/webp'
    assert response.headers['cache-control'] == 'public, max-age=31536000, immutable'
    assert len(response.content) > 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    'format_param,expected_content_type,expected_format',
    [
        ('webp', 'image/webp', 'WEBP'),
        ('jpeg', 'image/jpeg', 'JPEG'),
        ('png', 'image/png', 'PNG'),
    ],
)
def test_image_format_conversion(
    get_user,
    get_webpage,
    save_test_image_to_storage,
    format_param,
    expected_content_type,
    expected_format,
):
    """
    Test image conversion to different formats
    """
    path = save_test_image_to_storage(f'webpage/{get_webpage.id}/format.png')

    response = client.get(f'/image/{path}?f={format_param}', user=get_user)

    assert response.status_code == 200
    assert response.headers['content-type'] == expected_content_type

    image = Image.open(io.BytesIO(response.content))
    assert image.format == expected_format


@pytest.mark.django_db
@pytest.mark.parametrize(
    'mode',
    ['RGBA', 'LA', 'P'],
)
def test_image_jpeg_mode_conversion(get_user, get_webpage, save_test_image_to_storage, mode):
    """
    Test that images with transparency/palette are converted to RGB for JPEG
    """
    color = (255, 0, 0, 128) if mode == 'RGBA' else 255
    path = save_test_image_to_storage(f'webpage/{get_webpage.id}/mode.png', mode=mode, color=color)

    response = client.get(f'/image/{path}?f=jpeg', user=get_user)

    assert response.status_code == 200
    image = Image.open(io.BytesIO(response.content))
    assert image.mode == 'RGB'


@pytest.mark.django_db
def test_image_quality_adjustment(get_user, get_webpage, save_test_image_to_storage):
    """
    Test quality parameter affects output size
    """
    path = save_test_image_to_storage(f'webpage/{get_webpage.id}/quality.png')

    response_low = client.get(f'/image/{path}?f=jpeg&q=10', user=get_user)
    response_high = client.get(f'/image/{path}?f=jpeg&q=95', user=get_user)

    assert response_low.status_code == 200
    assert response_high.status_code == 200
    assert len(response_low.content) < len(response_high.content)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'params,expected_size',
    [
        ('w=400', (400, 300)),
        ('h=300', (400, 300)),
        ('w=200&h=100', (200, 100)),
    ],
)
def test_image_resize(get_user, get_webpage, save_test_image_to_storage, params, expected_size):
    """
    Test image resizing with different parameter combinations
    """
    path = save_test_image_to_storage(f'webpage/{get_webpage.id}/resize.png', size=(800, 600))

    response = client.get(f'/image/{path}?{params}&f=png', user=get_user)

    assert response.status_code == 200
    image = Image.open(io.BytesIO(response.content))
    assert image.size == expected_size


@pytest.mark.django_db
def test_image_no_resize_preserves_size(get_user, get_webpage, save_test_image_to_storage):
    """
    Test that image size is preserved when no resize params provided
    """
    original_size = (800, 600)
    path = save_test_image_to_storage(f'webpage/{get_webpage.id}/no_resize.png', size=original_size)

    response = client.get(f'/image/{path}?f=png', user=get_user)

    assert response.status_code == 200
    image = Image.open(io.BytesIO(response.content))
    assert image.size == original_size


@pytest.mark.django_db
@pytest.mark.parametrize(
    'param,value,expected_status',
    [
        ('w', 0, 422),
        ('w', -1, 422),
        ('w', 3841, 422),
        ('w', 1920, 200),
        ('h', 0, 422),
        ('h', -1, 422),
        ('h', 2161, 422),
        ('h', 1080, 200),
        ('q', 0, 422),
        ('q', 101, 422),
        ('q', 50, 200),
    ],
)
def test_image_parameter_validation(
    get_user, get_webpage, save_test_image_to_storage, param, value, expected_status
):
    """
    Test validation of width, height, and quality parameters
    """
    path = save_test_image_to_storage(f'webpage/{get_webpage.id}/validation.png')

    response = client.get(f'/image/{path}?{param}={value}', user=get_user)

    assert response.status_code == expected_status


@pytest.mark.django_db
def test_image_invalid_format(get_user, get_webpage, save_test_image_to_storage):
    """
    Test that invalid format parameter returns validation error
    """
    path = save_test_image_to_storage(f'webpage/{get_webpage.id}/invalid_format.png')

    response = client.get(f'/image/{path}?f=bmp', user=get_user)

    assert response.status_code == 422


@pytest.mark.django_db
@pytest.mark.parametrize(
    'malicious_path',
    [
        '../../../etc/passwd',
        '../../secrets.txt',
        '/etc/passwd',
        '/absolute/path/to/file',
    ],
)
def test_image_path_traversal_protection(get_user, malicious_path):
    """
    Test that path traversal attempts are blocked
    """
    response = client.get(f'/image/{malicious_path}', user=get_user)

    assert response.status_code == 400
    assert response.json() == {'detail': 'Invalid path'}


@pytest.mark.django_db
@patch('base.api.image.django.core.files.storage.default_storage.open')
def test_image_corrupt_file_error(mock_open, get_user, get_webpage):
    """
    Test that corrupt/invalid image files return 400 error
    """
    mock_file = MagicMock()
    mock_file.__enter__ = Mock(return_value=io.BytesIO(b'not an image'))
    mock_file.__exit__ = Mock(return_value=False)
    mock_open.return_value = mock_file

    response = client.get(f'/image/webpage/{get_webpage.id}/corrupt.png', user=get_user)

    assert response.status_code == 400
    assert response.json()['detail'] == 'Error processing image'


@pytest.mark.parametrize(
    'width,height,expected_size',
    [
        (400, 200, (400, 200)),
        (400, None, (400, 300)),
        (None, 300, (400, 300)),
        (None, None, (800, 600)),
    ],
)
def test_resize_image_function(width, height, expected_size):
    """
    Test resize_image helper function with different parameter combinations
    """
    image = Image.new('RGB', (800, 600))

    resized = resize_image(image, width=width, height=height)

    assert resized.size == expected_size


def test_resize_image_no_update_returns_same_instance():
    """
    Test that resize_image returns the same instance when no resize needed
    """
    image = Image.new('RGB', (800, 600))

    resized = resize_image(image, width=None, height=None)

    assert resized is image


@pytest.mark.parametrize(
    'format_type,expected_pil_format,expected_content_type',
    [
        ('webp', 'WEBP', 'image/webp'),
        ('avif', 'AVIF', 'image/avif'),
        ('jpeg', 'JPEG', 'image/jpeg'),
        ('png', 'PNG', 'image/png'),
        (None, 'WEBP', 'image/webp'),
        ('invalid', 'WEBP', 'image/webp'),
    ],
)
def test_get_format_config(format_type, expected_pil_format, expected_content_type):
    """
    Test get_format_config helper function for all format types
    """
    pil_format, content_type = get_format_config(format_type)

    assert pil_format == expected_pil_format
    assert content_type == expected_content_type


@pytest.mark.django_db
def test_image_rejects_oversized_source_dimensions(get_user, get_webpage, create_test_image):
    """
    Test that images with source dimensions exceeding 3840px are rejected
    """
    large_image_bytes = create_test_image(size=(4000, 100))
    path = f'webpage/{get_webpage.id}/large.png'
    default_storage.save(path, ContentFile(large_image_bytes))

    response = client.get(f'/image/{path}', user=get_user)

    assert response.status_code == 400
    assert response.json()['detail'] == 'Source image dimensions exceed limits'

    default_storage.delete(path)
