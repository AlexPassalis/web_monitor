from django.urls import path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.svg', permanent=True)),
    path('', views.home, name='home'),
]
