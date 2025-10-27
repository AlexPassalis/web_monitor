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

DB_HOST = validate_env('POSTGRES_HOST')
DB_PORT = validate_env('POSTGRES_PORT')

DB_NAME = validate_env('POSTGRES_DB')
DB_USER = validate_env('POSTGRES_USER')
DB_PASSWORD = validate_env('POSTGRES_PASSWORD')
ALLOWED_HOSTS = [host.strip() for host in validate_env('ALLOWED_HOSTS').split(',')]
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in validate_env('CORS_ALLOWED_ORIGINS').split(',')]
