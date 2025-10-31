from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def run_every_minute():
    logger.info('Task running every minute')
    pass


@shared_task
def run_every_hour():
    logger.info('Task running every hour')
    pass


@shared_task
def run_every_day():
    logger.info('Task running every day')
    pass
