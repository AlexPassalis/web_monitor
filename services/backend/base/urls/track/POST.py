from . import router
from django.http import HttpRequest
from .schemas import TrackRequest, TrackResponse, ValidationErrorResponse


@router.post(
    '/track',
    url_name='track',
    response={201: TrackResponse, 422: ValidationErrorResponse},
)
def track(request: HttpRequest, data: TrackRequest) -> tuple[int, dict[str, str]]:
    return 201, {'message': 'URL tracked successfully', 'url': str(data.url)}
