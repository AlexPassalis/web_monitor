from ninja import Router, Schema
from pydantic import HttpUrl
from typing import Literal
from django.http import HttpRequest
from base.models import TrackedWebsite
from base.tasks import create_initial_screenshot

router = Router(tags=['Tracking'])


class TrackRequest(Schema):
    url: HttpUrl
    interval: Literal['minute', 'hour', 'day']


class TrackResponse(Schema):
    message: Literal['URL tracked successfully']


class ValidationErrorResponse(Schema):
    detail: list[dict]


@router.post(
    '/track',
    response={
        422: ValidationErrorResponse,
        201: TrackResponse,
    },
)
def create_tracking(
    request: HttpRequest,
    data: TrackRequest,
) -> tuple[Literal[422], ValidationErrorResponse] | tuple[Literal[201], TrackResponse]:
    """Track a new URL for monitoring."""
    url = str(data.url)

    tracked_website, created = TrackedWebsite.objects.get_or_create(
        url=url,
    )  # TODO add the User in min, hour or day.

    if created:
        create_initial_screenshot.apply_async(
            args=(tracked_website.id, url),
            queue='high_priority',
        )

    return 201, TrackResponse(
        message='URL tracked successfully',
    )
