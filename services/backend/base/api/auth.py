from ninja import Router, Schema
from django.http import HttpRequest
from typing import Literal
import django.contrib.auth

router_auth = Router(tags=['Authentication'])


class LoginRequest(Schema):
    username: str
    password: str


class LoginResponse(Schema):
    message: Literal['Login successful']


class LogoutResponse(Schema):
    message: Literal['Logout successful']


class ErrorResponse(Schema):
    detail: str


@router_auth.post(
    '/login',
    response={
        200: LoginResponse,
        401: ErrorResponse,
    },
)
def login(
    request: HttpRequest,
    data: LoginRequest,
) -> tuple[Literal[200], LoginResponse] | tuple[Literal[401], ErrorResponse]:
    """
    Log a user in
    """

    user = django.contrib.auth.authenticate(request, username=data.username, password=data.password)

    if user is None:
        return 401, ErrorResponse(detail='Invalid username or password')

    django.contrib.auth.login(request, user)
    return 200, LoginResponse(message='Login successful')


@router_auth.post(
    '/logout',
    response={
        200: LogoutResponse,
    },
)
def logout(request: HttpRequest) -> tuple[Literal[200], LogoutResponse]:
    """
    Log the current user out
    """

    django.contrib.auth.logout(request)
    return 200, LogoutResponse(message='Logout successful')


@router_auth.get('/crsf', response={200: dict})
def get_crsf(request: HttpRequest) -> tuple[Literal[200], dict]:
    """
    Get CSRF token
    """

    return 200, {'csrfToken': request.META.get('CSRF_COOKIE')}
