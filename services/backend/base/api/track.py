from ninja import Router, Schema
from ninja.security import django_auth
from pydantic import HttpUrl
from typing import Literal
from base.request import AuthenticatedRequest
from base.models import Webpage
from base.tasks import create_initial_screenshot

router = Router(tags=['Webpage tracking'])

class TrackRequest(Schema):
    url: HttpUrl
    interval: Literal['minute', 'hour', 'day']


class TrackResponse(Schema):
    message: Literal['Webpage tracked successfully']


class ValidationErrorResponse(Schema):
    detail: list[dict]


class UnauthorizedResponse(Schema):
    detail: str


@router.post(
    '/track',
    auth=django_auth,
    response={
        401: UnauthorizedResponse,
        422: ValidationErrorResponse,
        201: TrackResponse,
    },
)
def add_webpage(
    request: AuthenticatedRequest,
    data: TrackRequest,
) -> (
    tuple[Literal[401], UnauthorizedResponse]
    | tuple[Literal[422], ValidationErrorResponse]
    | tuple[Literal[201], TrackResponse]
):
    url = str(data.url)
    user = request.auth

    tracked_website, created = Webpage.objects.get_or_create(url=url)
    getattr(tracked_website, data.interval).add(user)

    if created:
        create_initial_screenshot.apply_async(
            args=(tracked_website.id, url),
            queue='high_priority',
        )

    return 201, TrackResponse(
        message='Webpage tracked successfully',
    )
