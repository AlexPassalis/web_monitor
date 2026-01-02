FROM python:3.13.3-slim AS base
ENV DJANGO_SETTINGS_MODULE=config.settings
ENV HOST=0.0.0.0
ENV PORT=8000
# Set Playwright to use root's cache
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright



FROM base AS deps
WORKDIR /app
USER root
# Add system build deps for psycopg[c] + curl for the installer
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    pkg-config \
    curl \
    ca-certificates
# Download the uv installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh
# Run the installer and remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh
# Ensure uv binary is in PATH
ENV PATH="/root/.local/bin/:$PATH"
COPY pyproject.toml uv.lock ./



FROM deps AS deps-dev
RUN uv sync --frozen --no-cache --extra dev
# Install Playwright
RUN uv run playwright install --with-deps chromium



FROM deps AS deps-prod
RUN uv sync --frozen --no-cache --no-dev
# Install Playwright
RUN uv run playwright install --with-deps chromium



FROM deps-dev AS dev
# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
# Make uv cache directory accessible to appuser
RUN mkdir -p /home/appuser/.cache/uv && chown -R appuser:appuser /home/appuser/.cache
# Make Playwright cache accessible to appuser
RUN mkdir -p /app && chown -R appuser:appuser /app
RUN chmod 711 /root && \
    find /root/.cache -type d -exec chmod 755 {} + && \
    find /root/.cache -type f -executable -exec chmod 755 {} + && \
    find /root/.cache -type f ! -executable -exec chmod 644 {} +

COPY --chown=appuser:appuser . .

USER appuser

ENV ENV=development
ENV ALLOWED_HOSTS=localhost,127.0.0.1,${HOST}
ENV TRUSTED_ORIGINS=https://localhost,http://localhost:${PORT},http://localhost:3000
# Prevent python from creating __pycache__ files
ENV PYTHONDONTWRITEBYTECODE=1
# Default init command, is overriden for the worker and beat service in the docker-stac file
CMD ["sh", "-c", "uv run gunicorn config.wsgi:application --bind ${HOST}:${PORT} --reload"]



FROM deps-prod AS prod
# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
# Make uv cache directory accessible to appuser
RUN mkdir -p /home/appuser/.cache/uv && chown -R appuser:appuser /home/appuser/.cache
# Make Playwright cache accessible to appuser
RUN mkdir -p /app && chown -R appuser:appuser /app
RUN chmod 711 /root && \
    find /root/.cache -type d -exec chmod 755 {} + && \
    find /root/.cache -type f -executable -exec chmod 755 {} + && \
    find /root/.cache -type f ! -executable -exec chmod 644 {} +

COPY --chown=appuser:appuser . .
RUN chmod +x /app/migrate

USER appuser

ENV ENV=production
ENV ALLOWED_HOSTS=
ENV CORS_ALLOWED_ORIGINS=
# Default init command, is overriden for the worker and beat service in the docker-stac file
CMD ["sh", "-c", "uv run gunicorn config.wsgi:application --bind ${HOST}:${PORT}"]
