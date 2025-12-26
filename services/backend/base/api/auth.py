from ninja import Router, Schema
from django.http import HttpRequest
from typing import Literal
import django.contrib.auth
from base.models import User
from django.core.exceptions import ValidationError
from django.middleware.csrf import get_token

router_auth = Router(tags=['Authentication'])


class Request:
    class Signup(Schema):
        username: str
        password: str

    class Login(Schema):
        username: str
        password: str


class Response:
    class Signup(Schema):
        message: Literal['User created successfully']

    class Login(Schema):
        message: Literal['Login successful']

    class Logout(Schema):
        message: Literal['Logout successful']

    class Error(Schema):
        detail: str | dict | list


@router_auth.post(
    '/signup',
    response={
        201: Response.Signup,
        400: Response.Error,
    },
)
def signup(
    request: HttpRequest,
    data: Request.Signup,
) -> tuple[Literal[201], Response.Signup] | tuple[Literal[400], Response.Error]:
    """
    Create a new user account
    """

    try:
        user = User.objects.create_user(username=data.username, password=data.password)
    except ValidationError as error:
        return 400, Response.Error(detail=error.messages)

    django.contrib.auth.login(request, user)

    return 201, Response.Signup(message='User created successfully')


@router_auth.post(
    '/login',
    response={
        200: Response.Login,
        401: Response.Error,
    },
)
def login(
    request: HttpRequest,
    data: Request.Login,
) -> tuple[Literal[200], Response.Login] | tuple[Literal[401], Response.Error]:
    """
    Log a user in
    """

    user = django.contrib.auth.authenticate(request, username=data.username, password=data.password)

    if user is None:
        return 401, Response.Error(detail='Invalid username or password')

    django.contrib.auth.login(request, user)
    return 200, Response.Login(message='Login successful')


@router_auth.post(
    '/logout',
    response={
        200: Response.Logout,
    },
)
def logout(request: HttpRequest) -> tuple[Literal[200], Response.Logout]:
    """
    Log the current user out
    """

    django.contrib.auth.logout(request)
    return 200, Response.Logout(message='Logout successful')


@router_auth.get('/csrf', response={200: dict})
def get_csrf(request: HttpRequest) -> tuple[Literal[200], dict]:
    """
    Get CSRF token
    """

    return 200, {'csrfToken': get_token(request)}
