from ninja import NinjaAPI
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import URLResolver, path

from .track import router_track

api: NinjaAPI = NinjaAPI(
    title='Backend Service API',
    version='1.0.0',
    description='API for tracking and monitoring services',
)


@api.get('/favicon.ico', url_name='favicon', include_in_schema=False)
def favicon(request: HttpRequest) -> HttpResponse:
    return redirect('/static/favicon.svg', permanent=True)


@api.get('/', url_name='home')
def home(request: HttpRequest) -> dict[str, str]:
    return {'message': 'Welcome to the Backend Service!'}


api.add_router('', router_track)

urlpatterns: list[URLResolver] = [
    path('', api.urls),
]
