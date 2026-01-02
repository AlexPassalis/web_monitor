from celery import Celery

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'run-every-minute': {
        'task': 'base.tasks.tasks_beat.run_every_minute',
        'schedule': 60.0,  # every 60 seconds
        'options': {'queue': 'high_priority'},
    },
}

app.autodiscover_tasks()

app.conf.imports = ('base.tasks.tasks_beat',)

app.conf.worker_prefetch_multiplier = 1
app.conf.worker_concurrency = 2
app.conf.worker_pool = 'threads'
