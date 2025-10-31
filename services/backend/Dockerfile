FROM python:3.13.3-slim AS base
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DJANGO_SETTINGS_MODULE=config.settings


FROM base AS deps
WORKDIR /app
USER root
# Upgrade pip tooling once
RUN python -m pip install --upgrade --no-cache-dir pip setuptools wheel
# Add system build deps for psycopg[c]
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev pkg-config

COPY requirements/ requirements/



FROM deps AS deps-dev
RUN python3 -m pip install -r requirements/development.txt
# Install Playwright browsers
RUN playwright install --with-deps chromium


FROM deps AS deps-prod
RUN python3 -m pip install -r requirements/production.txt
# Install Playwright browsers
RUN playwright install --with-deps chromium



FROM deps-dev AS dev
# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN mkdir -p /app && chown -R appuser:appuser /app

COPY --chown=appuser:appuser . .

USER appuser

ENV ENV=development
ENV ALLOWED_HOSTS=localhost,127.0.0.1,${HOST}
ENV CORS_ALLOWED_ORIGINS=http://localhost:${PORT}

# Default init command, is overriden for the worker and beat service in the docker-compose file.
CMD ["sh", "-c", "uvicorn config.asgi:application --host ${HOST} --port ${PORT} --reload"]



FROM deps-prod AS prod
# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN mkdir -p /app && chown -R appuser:appuser /app

COPY --chown=appuser:appuser . .

USER appuser

ENV ENV=production
ENV ALLOWED_HOSTS=
ENV CORS_ALLOWED_ORIGINS=

# Optional but recommended if you use WhiteNoise/static: TODO try to see if it runs without it.
# RUN python manage.py collectstatic --noinput

# Default init command, is overriden for the worker and beat service in the docker-compose file.
CMD ["sh","-c","exec gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -b ${HOST}:${PORT} --workers 3 --timeout 60"]
