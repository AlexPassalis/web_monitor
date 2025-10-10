from typing import TypedDict, NotRequired
from base.utils import min_passed
from django.shortcuts import render


class Update(TypedDict):
    name: str
    status: str
    timestamp: str
    mins_ago: NotRequired[int]


# Create your views here.
def home(request):
    latest_updates: list[Update] = [
        {
            'name': 'E2E Prod',
            'status': 'SUCCESS',
            'timestamp': '2025-09-27T14:57:00Z',
        },
        {
            'name': 'E2E Staging',
            'status': 'SUCCESS',
            'timestamp': '2025-09-27T14:57:00Z',
        },
        {
            'name': 'E2E Staging',
            'status': 'SUCCESS',
            'timestamp': '2025-09-27T14:57:00Z',
        },
        {
            'name': 'E2E Prod',
            'status': 'SUCCESS',
            'timestamp': '2025-09-27T14:57:00Z',
        },
        {
            'name': 'Pipeline Staging',
            'status': 'SUCCESS',
            'timestamp': '2025-09-27T14:57:00Z',
        },
        {
            'name': 'Pipeline production',
            'status': 'Error loading',
            'timestamp': '2025-09-27T14:57:00Z',
        },
        {
            'name': 'Repo Linter',
            'status': 'FAILURE',
            'timestamp': '2025-09-27T14:57:00Z',
        },
        {
            'name': 'Disaster Recovery Backup',
            'status': 'SUCCESS',
            'timestamp': '2025-09-27T14:57:00Z',
        },
    ]
    for update in latest_updates:
        update['mins_ago'] = min_passed(update['timestamp'])
    return render(request, 'home.html', {'latest_updates': latest_updates})
