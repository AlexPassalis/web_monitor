import json
from ninja import Schema
from pydantic import HttpUrl

from . import router_track
from django.http import HttpRequest
from playwright.sync_api import sync_playwright


class TrackRequest(Schema):
    url: HttpUrl


class TrackResponse(Schema):
    message: str
    url: str


class ValidationErrorResponse(Schema):
    detail: list[dict]


@router_track.post(
    path='/track',
    response={201: TrackResponse, 422: ValidationErrorResponse},
)
def track(
    request: HttpRequest,
    data: TrackRequest,
) -> tuple[int, TrackResponse | ValidationErrorResponse]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(str(data.url))
        print(
            page.content(),
        )
        browser.close()

    return 201, TrackResponse(message='URL tracked successfully', url=str(data.url))
