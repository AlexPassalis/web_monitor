import os


def validate_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f'Missing environment variable: {name}.')
    return value
