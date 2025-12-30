from django.urls import URLResolver, path
from ninja import NinjaAPI

from .add_webpage import router_add_webpage
from .auth import router_auth
from .favicon_ico import router_favicon
from .health import router_health

api: NinjaAPI = NinjaAPI(
    title='Backend API Service',
    version='0.0.1',
    description='API for tracking webpage changes',
)

api.add_router('/', router_health)
api.add_router('', router_favicon)
api.add_router('/', router_auth)
api.add_router('/', router_add_webpage)

urlpatterns: list[URLResolver] = [
    path('', api.urls),
]
