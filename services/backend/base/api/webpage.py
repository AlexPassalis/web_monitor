from typing import Annotated, Literal

from django.http import HttpRequest
from ninja import Query, Router, Schema
from ninja.security import django_auth
from pydantic import Field, HttpUrl

from base.models import Webpage, WebpageScreenshot, WebpageTracking

path = '/webpage'

router_webpage = Router(tags=['Webpage tracking'])


class TrackRequest(Schema):
    url: Annotated[HttpUrl, Field(max_length=2048)]
    interval: Literal['minute', 'hour', 'day']


class TrackResponse(Schema):
    message: Literal['Webpage tracked successfully']
    interval: Literal['minute', 'hour', 'day']
    url: str
    id: int


class ValidationErrorResponse(Schema):
    detail: list[dict]


class UnauthorizedResponse(Schema):
    detail: str


@router_webpage.post(
    summary='Add new webpage to track',
    auth=django_auth,
    path=path,
    response={
        401: UnauthorizedResponse,
        422: ValidationErrorResponse,
        201: TrackResponse,
    },
)
def webpage_post(
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

    webpage, webpage_created = Webpage.objects.get_or_create(url=url)

    WebpageTracking.objects.update_or_create(
        webpage=webpage,
        user=user,
        defaults={'interval': interval},
    )

    if webpage_created:
        WebpageScreenshot.save_screenshot.apply_async(
            args=(webpage.id,),
            queue='high_priority',
        )

    return 201, TrackResponse(
        message='Webpage tracked successfully',
        interval=interval,
        url=webpage.url,
        id=webpage.id,
    )


class WebpageDetail(Schema):
    interval: Literal['minute', 'hour', 'day']
    url: str
    id: int
    screenshots: list[str]


WebpageListResponse = list[WebpageDetail]


class WebpageGetQuery(Schema):
    interval: Literal['minute', 'hour', 'day'] | None = None


@router_webpage.get(
    summary='Get tracked webpages',
    auth=django_auth,
    path=path,
    response={
        401: UnauthorizedResponse,
        200: WebpageListResponse,
    },
)
def webpage_get(
    request: HttpRequest,
    query: Query[WebpageGetQuery],
) -> tuple[Literal[401], UnauthorizedResponse] | tuple[Literal[200], WebpageListResponse]:
    """
    Get all webpages that the user is tracking for the specified interval or all intervals
    """
    assert request.user.is_authenticated

    user = request.user
    interval = query.interval

    if interval:
        webpage_trackings = WebpageTracking.objects.filter(
            user=user, interval=interval
        ).select_related('webpage')
    else:
        webpage_trackings = WebpageTracking.objects.filter(user=user).select_related('webpage')

    all_webpages = []
    for webpage_tracking in webpage_trackings:
        screenshots_created_at = webpage_tracking.webpage.get_screenshots_created_at(limit=10)
        all_webpages.append(
            WebpageDetail(
                interval=webpage_tracking.interval,
                url=webpage_tracking.webpage.url,
                id=webpage_tracking.webpage.id,
                screenshots=screenshots_created_at,
            )
        )

    return 200, all_webpages


class DeleteRequest(Schema):
    id: int


class DeleteResponse(Schema):
    message: Literal['Webpage tracking removed successfully']
    id: int
    url: str


@router_webpage.delete(
    summary='Remove webpage from being tracked',
    auth=django_auth,
    path=path,
    response={
        401: UnauthorizedResponse,
        404: ValidationErrorResponse,
        200: DeleteResponse,
    },
)
def webpage_delete(
    request: HttpRequest,
    data: DeleteRequest,
) -> (
    tuple[Literal[401], UnauthorizedResponse]
    | tuple[Literal[404], ValidationErrorResponse]
    | tuple[Literal[200], DeleteResponse]
):
    """
    Remove a webpage from user's tracking list
    """
    assert request.user.is_authenticated

    user = request.user
    webpage_id = data.id

    webpage_tracking = (
        WebpageTracking.objects.filter(webpage__id=webpage_id, user=user)
        .select_related('webpage')
        .first()
    )

    if not webpage_tracking:
        return 404, ValidationErrorResponse(
            detail=[
                {
                    'loc': ['body', 'id'],
                    'msg': 'You are not tracking this webpage',
                    'type': 'value_error',
                },
            ],
        )

    webpage_id = webpage_tracking.webpage.id
    webpage_url = webpage_tracking.webpage.url
    webpage_tracking.delete()

    return 200, DeleteResponse(
        message='Webpage tracking removed successfully', id=webpage_id, url=webpage_url
    )
