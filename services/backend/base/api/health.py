from ninja import Router, Schema
from django.http import HttpRequest


router = Router()


class HealthResponse(Schema):
    status: str


@router.get(
    '/health',
    response={200: HealthResponse},
    include_in_schema=False,
)
def health_check(request: HttpRequest) -> tuple[int, HealthResponse]:
    """Health check endpoint for monitoring services like Render."""
    return 200, HealthResponse(status='ok')
