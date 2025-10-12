from os import environ
from utils.validate_env import validate_env

ENV = environ.get('ENV')

if ENV not in ('development', 'testing', 'production'):
    raise SystemExit(f'Invalid ENV value: {ENV}.')

DB_HOST = validate_env('POSTGRES_HOST')
DB_PORT = validate_env('POSTGRES_PORT')

DB_NAME = validate_env('POSTGRES_DB')
DB_USER = validate_env('POSTGRES_USER')
DB_PASSWORD = validate_env('POSTGRES_PASSWORD')
