from ninja import NinjaAPI
from django.urls import URLResolver, path

from .track import router as track_router
from .health import router as health_router
from .favicon_ico import router as favicon_router
from .auth import router as auth_router
from .csrf import router as csrf_router


api: NinjaAPI = NinjaAPI(
    title='Backend Service API',
    version='1.0.0',
    description='API for tracking and monitoring services',
    csrf=True,
)

api.add_router('', favicon_router)
api.add_router('/', health_router)
api.add_router('/', track_router)
api.add_router('/', auth_router)
api.add_router('/', csrf_router)

urlpatterns: list[URLResolver] = [
    path('', api.urls),
]
