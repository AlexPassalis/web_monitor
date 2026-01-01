from django.urls import URLResolver, path
from ninja import NinjaAPI

from .auth import router_auth
from .favicon_ico import router_favicon
from .health import router_health
from .image import router_image
from .webpage import router_webpage

api = NinjaAPI(
    title='Backend API Service',
    version='0.0.1',
    description='API for tracking webpage changes',
)

api.add_router('', router_favicon)
api.add_router('/', router_health)
api.add_router('/', router_auth)
api.add_router('/', router_webpage)
api.add_router('/', router_image)

urlpatterns: list[URLResolver] = [
    path('', api.urls),
]
