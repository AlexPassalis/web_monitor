from django.utils import timezone
from django.utils.dateparse import parse_datetime


def min_passed(ts: str) -> int:
    dt = parse_datetime(ts)
    if not dt:
        return 0
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.utc)
    return max(0, int((timezone.now() - dt).total_seconds() // 60))
