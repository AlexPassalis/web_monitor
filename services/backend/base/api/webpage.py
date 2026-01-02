from typing import Annotated, Literal

from django.http import HttpRequest
from ninja import Query, Router, Schema
from ninja.security import django_auth
from pydantic import Field, HttpUrl

from base.models import Webpage, WebpageMonitoring
from base.tasks.tasks import save_initial_screenshot

path = '/webpage'

router_webpage = Router(tags=['Webpage monitoring'])


class MonitorRequest(Schema):
    url: Annotated[HttpUrl, Field(max_length=2048)]
    interval: Literal['minute', 'hour', 'day']


class MonitorResponse(Schema):
    message: str
    interval: Literal['minute', 'hour', 'day']
    url: str
    id: int


class ValidationErrorResponse(Schema):
    detail: list[dict]


class UnauthorizedResponse(Schema):
    detail: str


@router_webpage.post(
    summary='Add a webpage to be monitored or update its interval',
    auth=django_auth,
    path=path,
    response={
        401: UnauthorizedResponse,
        422: ValidationErrorResponse,
        200: MonitorResponse,
        201: MonitorResponse,
    },
)
def webpage_post(
    request: HttpRequest,
    data: MonitorRequest,
) -> (
    tuple[Literal[401], UnauthorizedResponse]
    | tuple[Literal[422], ValidationErrorResponse]
    | tuple[Literal[200], MonitorResponse]
    | tuple[Literal[201], MonitorResponse]
):
    assert request.user.is_authenticated

    user = request.user
    url = str(data.url)
    interval = data.interval

    webpage, webpage_created = Webpage.objects.get_or_create(url=url)

    if webpage_created:
        save_initial_screenshot.apply_async(
            args=(webpage.id,),
            queue='high_priority',
        )

    monitoring, monitoring_created = WebpageMonitoring.objects.get_or_create(
        webpage=webpage,
        user=user,
        defaults={'interval': interval},
    )

    if monitoring_created:
        return 201, MonitorResponse(
            message='Webpage is now being monitored',
            interval=interval,
            url=webpage.url,
            id=webpage.id,
        )
    elif monitoring.interval == interval:
        return 200, MonitorResponse(
            message='Already monitoring this webpage with the same interval',
            interval=interval,
            url=webpage.url,
            id=webpage.id,
        )
    else:
        monitoring.interval = interval
        monitoring.save()
        return 200, MonitorResponse(
            message='Monitoring interval updated',
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
    summary='Get webpages being monitored by the user',
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
    Get all webpages that the user is monitoring for the specified interval or all intervals
    """
    assert request.user.is_authenticated

    user = request.user
    interval = query.interval

    if interval:
        webpage_monitorings = WebpageMonitoring.objects.filter(
            user=user, interval=interval
        ).select_related('webpage')
    else:
        webpage_monitorings = WebpageMonitoring.objects.filter(user=user).select_related('webpage')

    all_webpages = []
    for webpage_monitoring in webpage_monitorings:
        screenshots_created_at = webpage_monitoring.webpage.get_screenshots_created_at(limit=10)
        all_webpages.append(
            WebpageDetail(
                interval=webpage_monitoring.interval,  # type: ignore[arg-type]
                url=webpage_monitoring.webpage.url,
                id=webpage_monitoring.webpage.id,
                screenshots=screenshots_created_at,
            )
        )

    return 200, all_webpages


class DeleteRequest(Schema):
    id: int


class DeleteResponse(Schema):
    message: Literal['Webpage monitoring removed successfully']
    id: int
    url: str


@router_webpage.delete(
    summary='Remove a webpage from being monitored by the user',
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
    Remove a webpage from user's monitoring list
    """
    assert request.user.is_authenticated

    user = request.user
    webpage_id = data.id

    webpage_monitoring = (
        WebpageMonitoring.objects.filter(webpage__id=webpage_id, user=user)
        .select_related('webpage')
        .first()
    )

    if not webpage_monitoring:
        return 404, ValidationErrorResponse(
            detail=[
                {
                    'loc': ['body', 'id'],
                    'msg': 'You are not monitoring this webpage',
                    'type': 'value_error',
                },
            ],
        )

    webpage_id = webpage_monitoring.webpage.id
    webpage_url = webpage_monitoring.webpage.url
    webpage_monitoring.delete()

    return 200, DeleteResponse(
        message='Webpage monitoring removed successfully', id=webpage_id, url=webpage_url
    )
