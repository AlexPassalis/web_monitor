from ninja import Schema
from pydantic import HttpUrl

from . import router
from django.http import HttpRequest


class TrackRequest(Schema):
    url: HttpUrl


class TrackResponse(Schema):
    message: str
    url: str


class ValidationErrorResponse(Schema):
    detail: list[dict]


@router.post(
    '/track',
    url_name='track',
    response={201: TrackResponse, 422: ValidationErrorResponse},
)
def track(request: HttpRequest, data: TrackRequest) -> tuple[int, dict[str, str]]:
    return 201, {'message': 'URL tracked successfully', 'url': str(data.url)}
