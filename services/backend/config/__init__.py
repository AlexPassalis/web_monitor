import os
from os import environ


def validate_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f'Missing environment variable: {name}.')
    return value


ENV = environ.get('ENV')

if ENV not in ('development', 'testing', 'production'):
    raise SystemExit(f'Invalid ENV value: {ENV}.')

SECRET_KEY = validate_env('SECRET_KEY')
DEBUG = True if ENV != 'production' else False
LOG_LEVEL = 'DEBUG' if ENV == 'development' else 'INFO'

ALLOWED_HOSTS = [host.strip() for host in validate_env('ALLOWED_HOSTS').split(',')]
TRUSTED_ORIGINS = [origin.strip() for origin in validate_env('TRUSTED_ORIGINS').split(',')]

CORS_ALLOW_CREDENTIALS = True

DB_HOST = validate_env('POSTGRES_HOST')
DB_PORT = validate_env('POSTGRES_PORT')
DB_NAME = validate_env('POSTGRES_DB')
DB_USER = validate_env('POSTGRES_USER')
DB_PASSWORD = validate_env('POSTGRES_PASSWORD')

CELERY_BROKER_URL = validate_env('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = validate_env('CELERY_RESULT_BACKEND')

S3_ENDPOINT_URL = validate_env('S3_ENDPOINT_URL')
S3_ACCESS_KEY = validate_env('S3_ACCESS_KEY')
S3_SECRET_KEY = validate_env('S3_SECRET_KEY')
S3_BUCKET_NAME = validate_env('S3_BUCKET_NAME')
S3_REGION = validate_env('S3_REGION')
