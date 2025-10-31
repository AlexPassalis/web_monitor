from celery import shared_task


@shared_task
def run_every_minute():
    print('Task running every minute')
    pass


@shared_task
def run_every_hour():
    print('Task running every hour')
    pass


@shared_task
def run_every_day():
    print('Task running every day')
    pass
