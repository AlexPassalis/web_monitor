FROM python:3.13.3-slim AS base
ENV HOST=0.0.0.0
ENV PORT=8000



FROM base AS deps
WORKDIR /app
USER root

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
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE ${PORT}

CMD ["sh", "-c", "uvicorn config.asgi:application --host ${HOST} --port ${PORT} --reload"]
