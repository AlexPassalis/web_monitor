from ninja import Router
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect


router_favicon: Router = Router()


@router_favicon.get('/favicon.ico', include_in_schema=False)
def favicon(request: HttpRequest) -> HttpResponse:
    return redirect('/static/favicon.svg', permanent=True)
