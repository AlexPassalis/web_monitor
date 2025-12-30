from typing import Annotated, Literal

from django.http import HttpRequest
from ninja import Router, Schema
from ninja.security import django_auth
from pydantic import Field, HttpUrl

from base.models import Webpage, WebpageScreenshot

router_add_webpage = Router(tags=['Webpage tracking'])


class TrackRequest(Schema):
    url: Annotated[HttpUrl, Field(max_length=2048)]
    interval: Literal['minute', 'hour', 'day']


class TrackResponse(Schema):
    message: Literal['Webpage tracked successfully']


class ValidationErrorResponse(Schema):
    detail: list[dict]


class UnauthorizedResponse(Schema):
    detail: str


@router_add_webpage.post(
    '/add_webpage',
    auth=django_auth,
    response={
        401: UnauthorizedResponse,
        422: ValidationErrorResponse,
        201: TrackResponse,
    },
)
def add_webpage(
    request: HttpRequest,
    data: TrackRequest,
) -> (
    tuple[Literal[401], UnauthorizedResponse]
    | tuple[Literal[422], ValidationErrorResponse]
    | tuple[Literal[201], TrackResponse]
):
    assert request.user.is_authenticated

    user = request.user
    url = str(data.url)
    interval = data.interval

    tracked_webpage, created = Webpage.objects.get_or_create(url=url)
    match interval:
        case 'minute':
            tracked_webpage.minute.add(user)
        case 'hour':
            tracked_webpage.hour.add(user)
        case 'day':
            tracked_webpage.day.add(user)

    if created:
        WebpageScreenshot.save_screenshot.apply_async(
            args=(tracked_webpage.id, url),
            queue='high_priority',
        )

    return 201, TrackResponse(
        message='Webpage tracked successfully',
    )
