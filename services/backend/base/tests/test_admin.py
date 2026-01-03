import pytest
from django.contrib.admin.sites import AdminSite

from base.admin import WebpageAdmin
from base.models import User, Webpage, WebpageMonitoring
from conftest import TestValues


@pytest.mark.django_db
def test_webpage_admin_minute_count():
    """
    Test that minute_count returns correct count of minute interval monitorings
    """
    webpage = Webpage.objects.create(url=TestValues.url)
    other_webpage = Webpage.objects.create(url='https://other.com/')
    user_1 = User.objects.create_user(username='testuser1', password=TestValues.password)
    user_2 = User.objects.create_user(username='testuser2', password=TestValues.password)

    WebpageMonitoring.objects.create(webpage=webpage, user=user_1, interval='minute')
    WebpageMonitoring.objects.create(webpage=webpage, user=user_2, interval='minute')
    WebpageMonitoring.objects.create(webpage=other_webpage, user=user_1, interval='hour')

    admin = WebpageAdmin(Webpage, AdminSite())
    assert admin.minute_count(webpage) == 2


@pytest.mark.django_db
def test_webpage_admin_hour_count():
    """
    Test that hour_count returns correct count of hour interval monitorings
    """
    webpage = Webpage.objects.create(url=TestValues.url)
    other_webpage = Webpage.objects.create(url='https://other.com/')
    user_1 = User.objects.create_user(username='testuser1', password=TestValues.password)
    user_2 = User.objects.create_user(username='testuser2', password=TestValues.password)

    WebpageMonitoring.objects.create(webpage=webpage, user=user_1, interval='hour')
    WebpageMonitoring.objects.create(webpage=webpage, user=user_2, interval='minute')
    WebpageMonitoring.objects.create(webpage=other_webpage, user=user_1, interval='day')

    admin = WebpageAdmin(Webpage, AdminSite())
    assert admin.hour_count(webpage) == 1


@pytest.mark.django_db
def test_webpage_admin_day_count():
    """
    Test that day_count returns correct count of day interval monitorings
    """
    webpage = Webpage.objects.create(url=TestValues.url)
    other_webpage = Webpage.objects.create(url='https://other.com/')
    user_1 = User.objects.create_user(username='testuser1', password=TestValues.password)
    user_2 = User.objects.create_user(username='testuser2', password=TestValues.password)

    WebpageMonitoring.objects.create(webpage=webpage, user=user_1, interval='day')
    WebpageMonitoring.objects.create(webpage=webpage, user=user_2, interval='day')
    WebpageMonitoring.objects.create(webpage=other_webpage, user=user_1, interval='minute')

    admin = WebpageAdmin(Webpage, AdminSite())
    assert admin.day_count(webpage) == 2
