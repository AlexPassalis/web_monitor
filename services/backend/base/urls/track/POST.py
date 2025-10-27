from ninja import Schema
from pydantic import HttpUrl

from . import router_track
from django.http import HttpRequest


class TrackRequest(Schema):
    url: HttpUrl


class TrackResponse(Schema):
    message: str
    url: HttpUrl


class ValidationErrorResponse(Schema):
    detail: list[dict]


@router_track.post(
    '/track',
    url_name='track',
    response={201: TrackResponse, 422: ValidationErrorResponse},
)
def track(
    request: HttpRequest,
    data: TrackRequest,
) -> tuple[int, TrackResponse | ValidationErrorResponse]:
    return 201, TrackResponse(message='URL tracked successfully', url=data.url)
