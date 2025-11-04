from ninja import Router, Schema
from django.http import HttpRequest


router = Router(tags=['Health'])


class HealthResponse(Schema):
    status: str


@router.get('/health', response={200: HealthResponse})
def health_check(request: HttpRequest) -> tuple[int, HealthResponse]:
    """Health check endpoint for monitoring services like Render."""
    return 200, HealthResponse(status='ok')
