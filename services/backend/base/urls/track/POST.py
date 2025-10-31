from ninja import Schema
from pydantic import HttpUrl
from typing import Literal

from . import router_track
from django.http import HttpRequest
from base.models import TrackedWebsite
from playwright.sync_api import sync_playwright
from base.utils import get_html_content


class TrackRequest(Schema):
    url: HttpUrl
    interval: Literal['minute', 'hour', 'day']


class TrackResponse(Schema):
    message: Literal['URL tracked successfully']


class ValidationErrorResponse(Schema):
    detail: list[dict]


@router_track.post(
    path='/track',
    response={
        422: ValidationErrorResponse,
        201: TrackResponse,
    },
)
def track(
    request: HttpRequest,
    data: TrackRequest,
) -> tuple[Literal[422], ValidationErrorResponse] | tuple[Literal[201], TrackResponse]:
    url = str(data.url)

    tracked_website, created = TrackedWebsite.objects.get_or_create(
        url=url,
    )  # TODO add the User in min, hour or day.

    if created:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            html_content = get_html_content(browser, url)
            browser.close()

        tracked_website.snapshot.create(
            html_content=html_content,
        )

    return 201, TrackResponse(
        message='URL tracked successfully',
    )
