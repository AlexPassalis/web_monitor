from ninja import Router, Schema
from django.http import HttpRequest
from django.middleware.csrf import get_token
from typing import Literal


router = Router(tags=['CSRF'])


class CsrfTokenResponse(Schema):
    csrfToken: str


@router.get(
    '/csrf-token',
    response={
        200: CsrfTokenResponse,
    },
)
def get_csrf_token(
    request: HttpRequest,
) -> tuple[Literal[200], CsrfTokenResponse]:
    """Get CSRF token for authenticated requests."""

    token = get_token(request)
    return 200, CsrfTokenResponse(csrfToken=token)
