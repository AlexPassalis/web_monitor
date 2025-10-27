from ninja import NinjaAPI
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import URLPattern, path

from .track import router as track_router

api: NinjaAPI = NinjaAPI(
    title='Backend Service API',
    version='1.0.0',
    description='API for tracking and monitoring services',
)


@api.get('/favicon.ico', url_name='favicon')
def favicon(request: HttpRequest) -> HttpResponse:
    return redirect('/static/favicon.svg', permanent=True)


@api.get('/', url_name='home')
def home(request: HttpRequest) -> dict[str, str]:
    return {'message': 'Welcome to the Backend Service!'}


# Register routers
api.add_router('', track_router)

urlpatterns: list[URLPattern] = [
    path('', api.urls),
]
