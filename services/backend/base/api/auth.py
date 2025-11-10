from ninja import Router, Schema
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest
from typing import Literal


router = Router(tags=['Authentication'])


class LoginRequest(Schema):
    username: str
    password: str


class LoginResponse(Schema):
    message: Literal['Login successful']


class LogoutResponse(Schema):
    message: Literal['Logout successful']


class ErrorResponse(Schema):
    detail: str


@router.post(
    '/login',
    response={
        200: LoginResponse,
        401: ErrorResponse,
    },
)
def login_user(
    request: HttpRequest,
    data: LoginRequest,
) -> tuple[Literal[200], LoginResponse] | tuple[Literal[401], ErrorResponse]:
    """Log in a user with username and password."""

    user = authenticate(request, username=data.username, password=data.password)

    if user is None:
        return 401, ErrorResponse(detail='Invalid username or password')

    login(request, user)
    return 200, LoginResponse(message='Login successful')


@router.post(
    '/logout',
    response={
        200: LogoutResponse,
    },
)
def logout_user(request: HttpRequest) -> tuple[Literal[200], LogoutResponse]:
    """Log out the current user."""

    logout(request)
    return 200, LogoutResponse(message='Logout successful')
