from django.http import HttpRequest
from django.contrib.auth.models import User


class AuthenticatedRequest(HttpRequest):
    """HttpRequest with typed auth attribute for Django Ninja endpoints."""

    auth: User
