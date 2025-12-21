from ninja import Router, Schema
from django.http import HttpRequest

router_health = Router()


class HealthResponse(Schema):
    status: str


@router_health.get(
    '/health',
    response={200: HealthResponse},
    include_in_schema=False,
)
def health_check(request: HttpRequest) -> tuple[int, HealthResponse]:
    return 200, HealthResponse(status='ok')
