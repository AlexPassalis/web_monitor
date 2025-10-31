from celery import Celery
from celery.schedules import crontab

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'run-every-minute': {
        'task': 'base.tasks.run_every_minute',
        'schedule': 60.0,  # every 60 seconds
        'options': {'queue': 'high_priority'},
    },
    'run-every-hour': {
        'task': 'base.tasks.run_every_hour',
        'schedule': crontab(minute=0),  # every hour at minute 0
        'options': {'queue': 'medium_priority'},
    },
    'run-every-day': {
        'task': 'base.tasks.run_every_day',
        'schedule': crontab(hour=0, minute=0),  # every day at midnight
        'options': {'queue': 'low_priority'},
    },
}

app.autodiscover_tasks()
