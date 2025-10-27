FROM python:3.13.3-slim AS base
ENV HOST=0.0.0.0
ENV PORT=8000
EXPOSE ${PORT}



FROM base AS deps
WORKDIR /app
USER root

# Upgrade pip tooling once
RUN python -m pip install --upgrade --no-cache-dir pip setuptools wheel

# Add system build deps for psycopg[c]
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential libpq-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/



FROM deps AS deps-dev
RUN python3 -m pip install -r requirements/development.txt



FROM deps AS deps-prod
RUN python3 -m pip install -r requirements/production.txt



FROM deps-dev AS dev
COPY . .

ENV ENV=development
ENV ALLOWED_HOSTS=localhost,127.0.0.1,${HOST}
ENV CORS_ALLOWED_ORIGINS=http://localhost:${PORT}

CMD ["sh", "-c", "uvicorn config.asgi:application --host ${HOST} --port ${PORT} --reload"]



FROM deps-prod AS prod
COPY . .

ENV ENV=production

# Optional but recommended if you use WhiteNoise/static: TODO try to see if it runs without it.
# RUN python manage.py collectstatic --noinput

CMD ["sh","-c","exec gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -b ${HOST}:${PORT} --workers 3 --timeout 60"]
