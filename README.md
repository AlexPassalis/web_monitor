# Web Monitor

A full-stack web application that monitors webpages for visual updates by periodically taking screenshots and detecting differences using perceptual hashing. Users can register, log in, add URLs to monitor at configurable intervals, and view historical screenshots of detected updates.

[![CI](https://github.com/AlexPassalis/web_monitor/actions/workflows/CI.yml/badge.svg)](https://github.com/AlexPassalis/web_monitor/actions/workflows/CI.yml)
[![codecov](https://codecov.io/gh/AlexPassalis/web_monitor/branch/main/graph/badge.svg)](https://codecov.io/gh/AlexPassalis/web_monitor)

## How It Works

### Screenshot Capture & Update Detection

1. **User adds a URL** with a monitoring interval (minute, hour, or day)
2. **Initial screenshot** is queued as a high-priority Celery task
3. **Celery Beat** runs every 60 seconds, triggering screenshots for all pages due for capture
4. **Playwright** navigates to the URL and captures a full-page screenshot
5. **Perceptual hash** is computed using ImageHash library
6. **Hash comparison** with the previous screenshot determines if visual updates occurred
7. **Only new screenshots** are saved to S3, reducing storage and showing meaningful updates
8. **Users view history** through a carousel of detected updates

## Features

- **User Authentication** - Secure session-based authentication with CSRF protection
- **Webpage Monitoring** - Add URLs to monitor with configurable intervals (every minute, hour, or day)
- **Visual Update Detection** - Uses perceptual hashing to detect visual updates, not pixel-perfect differences
- **Screenshot History** - View carousel of historical screenshots showing detected updates
- **Image Optimization** - On-demand image resizing, format conversion (WebP, AVIF), and quality adjustment
  - The `/api/image/{path}` endpoint provides on-demand image optimization:
    - **Format conversion**: WebP, AVIF, JPEG, PNG
    - **Dynamic resizing**: Maintains aspect ratio, max 4K output
    - **Quality adjustment**: Configurable compression (1-100)
    - **Caching**: 1-year cache headers with Nginx 30-day cache layer
- **Real-time Task Processing** - Background screenshot capture with Celery task queues

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                    Client                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Nginx Gateway [:443]                                                       │
│  - SSL/TLS termination, HTTP/2                                              │
│  - Gzip compression, rate limiting                                          │
│  - Static & image caching                                                   │
│  - Reverse proxy                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                  ┌────────────────────┴────────────────────────┐
                  ▼                                             ▼
┌───────────────────────────────────┐       ┌───────────────────────────────────────┐
│  Frontend (React SPA) [:3000]     │       │   Backend (Django + Ninja) [:8000]    │
│  - User authentication UI         │       │   - REST API endpoints                │
│  - Dashboard & monitoring         │       │   - Session auth with CSRF            │
│  - Screenshot carousel            │       │   - Per-user data isolation           │
│  - Responsive design              │       │   - Image optimization                │
└───────────────────────────────────┘       └───────────────────────────────────────┘
                                                                │
                ┌────────────────────────────────────┬──────────┴─────────────────────────┐
                ▼                                    ▼                                    ▼
┌────────────────────────────────┐   ┌────────────────────────────────┐   ┌───────────────────────────────┐
│  PostgreSQL Database [:5432]   │   │  Valkey (Redis) Cache [:6379]  │   │  MinIO (S3) [:9000]           │
│  - User accounts               │   │  - Celery message broker       │   │  - Image files (screenshots)  │
│  - Webpage records             │   │  - Task result backend         │   │                               │
│  - Monitoring configs          │   │  - Session cache               │   │                               │
└────────────────────────────────┘   └────────────────────────────────┘   └───────────────────────────────┘
                                                │
                                                ▼
                    ┌───────────────────────────────────────────────────────┐
                    │  Celery Workers                                       │
                    │  - Celery Beat: Scheduled tasks (every minute)        │
                    │  - Workers: Screenshot capture, S3 cleanup            │
                    │  - Priority queues: high, medium, low                 │
                    └───────────────────────────────────────────────────────┘
                                                │
                                                ▼
                    ┌───────────────────────────────────────────────────────┐
                    │  Playwright Browser                                   │
                    │  - Headless Chromium for screenshot capture           │
                    │  - Full-page screenshots at 1920x1080                 │
                    │  - 10-second page load timeout                        │
                    └───────────────────────────────────────────────────────┘
```

## Tech Stack

### Backend

| Technology                                                                                                   | Purpose                                            |
| ------------------------------------------------------------------------------------------------------------ | -------------------------------------------------- |
| [**Python 3.13**](https://www.python.org/)                                                                   | Core language                                      |
| [**Django 5.2**](https://www.djangoproject.com/)                                                             | Web framework                                      |
| [**Django Ninja**](https://django-ninja.dev/)                                                                | REST API with automatic OpenAPI schema generation  |
| [**PostgreSQL**](https://www.postgresql.org/)                                                                | Primary database                                   |
| [**Celery**](https://docs.celeryq.dev/) + [**Redis**](https://redis.io/)                                     | Distributed task queue for background processing   |
| [**Playwright**](https://playwright.dev/python/)                                                             | Headless browser automation for screenshot capture |
| [**Pillow**](https://pillow.readthedocs.io/) + [**ImageHash**](https://github.com/JohannesBuchner/imagehash) | Image processing and perceptual hashing            |
| [**MinIO (S3)**](https://min.io/)                                                                            | Object storage for screenshots                     |
| [**Gunicorn**](https://gunicorn.org/)                                                                        | Production WSGI server                             |

### Frontend

| Technology                                        | Purpose                                  |
| ------------------------------------------------- | ---------------------------------------- |
| [**TypeScript**](https://www.typescriptlang.org/) | Type-safe JavaScript                     |
| [**React 19**](https://react.dev/)                | UI framework                             |
| [**React Router 7**](https://reactrouter.com/)    | Client-side routing                      |
| [**Mantine 8**](https://mantine.dev/)             | Component library                        |
| [**Tailwind CSS 4**](https://tailwindcss.com/)    | Utility-first styling                    |
| [**Zod**](https://zod.dev/)                       | Runtime validation                       |
| [**Bun**](https://bun.sh/)                        | Dev server, bundler, and package manager |
| [**openapi-fetch**](https://openapi-ts.dev/)      | Type-safe API client from OpenAPI schema |

## CI/CD Pipeline

### Pull Request Checks

1. **Linting & Type Checking** - [Ruff](https://docs.astral.sh/ruff/), [MyPy](https://mypy.readthedocs.io/), [ESLint](https://eslint.org/), [openapi-ts](https://openapi-ts.dev/)
2. **Backend Tests** - [pytest](https://docs.pytest.org/) with coverage reporting
3. **Migration Tests** - Verify database migrations apply cleanly
4. **Frontend E2E Tests** - [Playwright](https://playwright.dev/) browser tests
5. **All checks must pass** before merge

### Deployment (on merge to main)

1. **Build [Docker](https://www.docker.com/) images** for all services
2. **Push to [GitHub Container Registry](https://github.com/AlexPassalis?tab=packages)** with commit SHA tags
3. **Deploy to VPS** using [Docker Swarm](https://docs.docker.com/engine/swarm/) stack deployment

## API Documentation

The API is documented using the OpenAPI specification and includes an interactive Swagger UI for testing endpoints.

- **Interactive Docs**: [https://alexpassalis.com/api/docs](https://alexpassalis.com/api/docs)
- **OpenAPI Schema**: [https://alexpassalis.com/api/openapi.json](https://alexpassalis.com/api/openapi.json)

## In Development

- [ ] **Hourly & daily monitoring intervals** - Currently only `run_every_minute` is implemented
- [ ] **WebSocket live updates** - Real-time frontend updates when screenshots are captured
- [ ] **Telegram notifications** - Send messages when visual updates are detected
- [ ] **Frontend UI improvements** - User logout functionality and enhanced screenshot modal viewing
