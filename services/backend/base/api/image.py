import io
import logging
import re
from typing import Annotated, Literal

import django.core.files.storage
from django.http import FileResponse, HttpRequest
from ninja import Query, Router, Schema
from ninja.security import django_auth
from PIL import Image
from PIL.Image import Image as PILImage
from pydantic import Field

logger = logging.getLogger(__name__)

router_image = Router(tags=['Image'])


class ImageQuery(Schema):
    w: Annotated[int | None, Field(gt=0, le=3840)] = None
    h: Annotated[int | None, Field(gt=0, le=2160)] = None
    q: Annotated[int | None, Field(ge=1, le=100)] = 75
    f: Literal['webp', 'avif', 'jpeg', 'png'] | None = 'webp'


class ErrorResponse(Schema):
    detail: str


@router_image.get(
    summary='Get optimized image',
    auth=django_auth,
    path='/image/{path:path}',
    response={
        401: ErrorResponse,
        404: ErrorResponse,
        400: ErrorResponse,
    },
    include_in_schema=True,
)
def image_get(
    request: HttpRequest,
    path: str,
    query: Query[ImageQuery],
) -> (
    FileResponse
    | tuple[Literal[401], ErrorResponse]
    | tuple[Literal[404], ErrorResponse]
    | tuple[Literal[400], ErrorResponse]
):
    """
    Serves optimized images with format conversion, resizing, and quality adjustment
    """
    assert request.user.is_authenticated

    path_pattern = re.compile(r'^webpage/\d+/[\w\-_.]+\.(png|jpg|jpeg|webp|avif)$')
    if not path_pattern.match(path):
        return 400, ErrorResponse(detail='Invalid path')

    width = query.w
    height = query.h
    quality = query.q
    output_format = query.f

    try:
        with django.core.files.storage.default_storage.open(path, 'rb') as image_file:
            image: PILImage = Image.open(image_file)

            max_source_dimension = 3840  # 4k limit
            if image.width > max_source_dimension or image.height > max_source_dimension:
                logger.warning(
                    'Image dimensions too large: %dx%d for path %s',
                    image.width,
                    image.height,
                    path,
                )
                return 400, ErrorResponse(detail='Source image dimensions exceed limits')

            if width or height:
                image = resize_image(image, width, height)

            output_buffer = io.BytesIO()
            save_format, content_type = get_format_config(output_format)

            if save_format in ['WEBP', 'AVIF']:
                image.save(output_buffer, format=save_format, quality=quality, method=6)
            elif save_format == 'JPEG':
                if image.mode in ('RGBA', 'LA', 'P'):
                    image = image.convert('RGB')
                image.save(output_buffer, format=save_format, quality=quality, optimize=True)
            else:
                image.save(output_buffer, format=save_format, optimize=True)

            output_buffer.seek(0)
    except FileNotFoundError:
        return 404, ErrorResponse(detail='Image not found')
    except Exception as err:
        logger.error('Error processing image %s: %s', path, err)
        return 400, ErrorResponse(detail='Error processing image')

    return FileResponse(
        output_buffer,
        content_type=content_type,
        headers={
            'Cache-Control': 'public, max-age=31536000, immutable',
        },
    )


def resize_image(image: PILImage, width: int | None, height: int | None) -> PILImage:
    """
    Resize image. Maintains aspect ratio when only one dimension is provided.
    When both dimensions are specified, resizes to exact dimensions (may distort).
    """
    original_width, original_height = image.size

    if width and height:
        target_width = width
        target_height = height
    elif width:
        aspect_ratio = original_height / original_width
        target_width = width
        target_height = int(width * aspect_ratio)
    elif height:
        aspect_ratio = original_width / original_height
        target_width = int(height * aspect_ratio)
        target_height = height
    else:
        return image

    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)


def get_format_config(format_type: str | None) -> tuple[str, str]:
    """
    Get PIL format and content type for the requested format
    """
    accepted_file_formats = {
        'webp': ('WEBP', 'image/webp'),
        'avif': ('AVIF', 'image/avif'),
        'jpeg': ('JPEG', 'image/jpeg'),
        'png': ('PNG', 'image/png'),
    }

    if format_type is None:
        return ('WEBP', 'image/webp')

    return accepted_file_formats.get(format_type, ('WEBP', 'image/webp'))
