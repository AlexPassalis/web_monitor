# Web Monitor

A full-stack web application that monitors webpages for visual changes by periodically taking screenshots and detecting differences using perceptual hashing. Users can register, log in, add URLs to monitor at configurable intervals, and view historical screenshots of detected changes.

[![CI](https://github.com/AlexPassalis/web_monitor/actions/workflows/CI.yml/badge.svg)](https://github.com/AlexPassalis/web_monitor/actions/workflows/CI.yml)
[![codecov](https://codecov.io/gh/AlexPassalis/web_monitor/branch/main/graph/badge.svg)](https://codecov.io/gh/AlexPassalis/web_monitor)

## Features

- **User Authentication** - Secure session-based authentication with CSRF protection
- **Webpage Monitoring** - Add URLs to monitor with configurable intervals (every minute, hour, or day)
- **Visual Change Detection** - Uses perceptual hashing to detect visual changes, not pixel-perfect differences
- **Screenshot History** - View carousel of historical screenshots showing detected changes
- **Image Optimization** - On-demand image resizing, format conversion (WebP, AVIF), and quality adjustment
- **Real-time Task Processing** - Background screenshot capture with Celery task queues

## Tech Stack

### Backend

| Technology             | Purpose                                            |
| ---------------------- | -------------------------------------------------- |
| **Python 3.13**        | Core language                                      |
| **Django 5.2**         | Web framework                                      |
| **Django Ninja**       | REST API with automatic OpenAPI schema generation  |
| **PostgreSQL**         | Primary database                                   |
| **Celery + Redis**     | Distributed task queue for background processing   |
| **Playwright**         | Headless browser automation for screenshot capture |
| **Pillow + ImageHash** | Image processing and perceptual hashing            |
| **MinIO (S3)**         | Object storage for screenshots                     |
| **Gunicorn + Uvicorn** | Production ASGI server                             |

### Frontend

| Technology         | Purpose                                  |
| ------------------ | ---------------------------------------- |
| **TypeScript**     | Type-safe JavaScript                     |
| **React 19**       | UI framework                             |
| **React Router 7** | Client-side routing                      |
| **Mantine 8**      | Component library                        |
| **Tailwind CSS 4** | Utility-first styling                    |
| **Zod**            | Runtime validation                       |
| **Bun**            | JavaScript runtime and package manager   |
| **openapi-fetch**  | Type-safe API client from OpenAPI schema |

### Infrastructure

| Technology                | Purpose                                 |
| ------------------------- | --------------------------------------- |
| **Docker & Docker Swarm** | Containerization and orchestration      |
| **Nginx**                 | Reverse proxy, SSL termination, caching |
| **GitHub Actions**        | CI/CD pipeline                          |
| **Valkey (Redis)**        | Caching and message broker              |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                   Client                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Nginx Gateway (443)                               │
│              SSL/TLS termination, static file caching, compression           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
┌───────────────────────────────┐       ┌───────────────────────────────────┐
│     Frontend (React SPA)       │       │      Backend (Django + Ninja)     │
│  - User authentication UI      │       │  - REST API endpoints             │
│  - Dashboard & monitoring      │       │  - Session authentication         │
│  - Screenshot carousel         │       │  - Image optimization             │
│  - Responsive design           │       │  - Business logic                 │
└───────────────────────────────┘       └───────────────────────────────────┘
                                                        │
                    ┌───────────────────────────────────┼───────────────────┐
                    ▼                                   ▼                   ▼
┌───────────────────────────┐   ┌───────────────────────────┐   ┌─────────────────┐
│    PostgreSQL Database     │   │    Valkey (Redis) Cache   │   │   MinIO (S3)    │
│  - User accounts           │   │  - Celery message broker  │   │  - Screenshots  │
│  - Webpage records         │   │  - Task result backend    │   │  - Image files  │
│  - Monitoring configs      │   │  - Session cache          │   │                 │
└───────────────────────────┘   └───────────────────────────┘   └─────────────────┘
                                            │
                                            ▼
                    ┌───────────────────────────────────────────────────────┐
                    │                  Celery Workers                        │
                    │  - Celery Beat: Scheduled tasks (every minute)         │
                    │  - Workers: Screenshot capture, S3 cleanup             │
                    │  - Priority queues: high, medium, low                  │
                    └───────────────────────────────────────────────────────┘
                                            │
                                            ▼
                    ┌───────────────────────────────────────────────────────┐
                    │               Playwright Browser                       │
                    │  - Headless Chromium for screenshot capture           │
                    │  - Full-page screenshots at 1920x1080                 │
                    │  - 10-second page load timeout                        │
                    └───────────────────────────────────────────────────────┘
```

## How It Works

### Screenshot Capture & Change Detection

1. **User adds a URL** with a monitoring interval (minute, hour, or day)
2. **Initial screenshot** is queued as a high-priority Celery task
3. **Celery Beat** runs every 60 seconds, triggering screenshots for all pages due for capture
4. **Playwright** navigates to the URL and captures a full-page screenshot
5. **Perceptual hash** is computed using ImageHash library
6. **Hash comparison** with the previous screenshot determines if visual changes occurred
7. **Only changed screenshots** are saved to S3, reducing storage and showing meaningful changes
8. **Users view history** through a carousel of detected changes

### Image Optimization Pipeline

The `/api/image/{path}` endpoint provides on-demand image optimization:

- **Format conversion**: WebP, AVIF, JPEG, PNG
- **Dynamic resizing**: Maintains aspect ratio, max 4K output
- **Quality adjustment**: Configurable compression (1-100)
- **Caching**: 1-year cache headers with Nginx 30-day cache layer

## Project Structure

```
web_monitor/
├── services/
│   ├── backend/              # Django application
│   │   ├── config/           # Settings, Celery config, URL routing
│   │   ├── base/             # Main Django app
│   │   │   ├── models/       # User, Webpage, WebpageMonitoring, WebpageScreenshot
│   │   │   ├── api/          # REST endpoints (auth, webpage, image, health)
│   │   │   └── tasks/        # Celery tasks (screenshot capture, cleanup)
│   │   └── Dockerfile        # Multi-stage build (dev/prod)
│   ├── gateway/
│   │   ├── frontend/         # React application
│   │   │   ├── src/app/      # Page components (Auth, Home, Error pages)
│   │   │   ├── src/lib/      # OpenAPI client, utilities
│   │   │   └── tests/        # Playwright E2E tests
│   │   └── nginx.conf        # Production proxy configuration
│   ├── db/                   # PostgreSQL configuration
│   ├── cache/                # Valkey (Redis) configuration
│   └── s3/                   # MinIO configuration
├── .github/
│   └── workflows/            # CI/CD pipelines
├── bin/                      # Helper scripts
├── docker-stack.yaml         # Production deployment
└── Makefile                  # Development commands
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Make (optional, for convenience commands)

### Development Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/AlexPassalis/web_monitor.git
   cd web_monitor
   ```

2. **Start all services**

   ```bash
   make start
   ```

   This creates the Docker network/volume if needed and starts all containers.

3. **Access the application**
   - Frontend: https://localhost (accepts self-signed cert)
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs

### Development Commands

```bash
# Service management
make start              # Start all Docker services
make stop               # Stop all services

# Backend development
make test_backend       # Run pytest
make lint_backend       # Run Ruff linter
make check_type_backend # Run MyPy type checker
make migrate            # Apply database migrations

# Frontend development
make install_frontend   # Install dependencies
make build_frontend     # Build production bundle
make test_frontend      # Run Playwright tests

# Run commands in containers
bin/dockerize_backend <command>   # Execute in backend container
bin/in_frontend <command>         # Execute in frontend environment
```

## Testing

### Backend Tests

```bash
make test_backend
```

- Uses pytest with pytest-django
- Parallel test execution enabled
- Coverage reports uploaded to Codecov

### Frontend Tests

```bash
make test_frontend
```

- Playwright browser automation
- E2E tests for authentication and main flows

## CI/CD Pipeline

### Pull Request Checks

1. **Linting & Type Checking** - Ruff and MyPy validation
2. **Backend Tests** - pytest with coverage reporting
3. **Migration Tests** - Verify database migrations apply cleanly
4. **Frontend E2E Tests** - Playwright browser tests

### Deployment (on merge to main)

1. **Build Docker images** for all services
2. **Push to GitHub Container Registry** with commit SHA tags
3. **Deploy to VPS** using Docker Swarm stack deployment

## API Endpoints

| Method | Endpoint            | Auth | Description                   |
| ------ | ------------------- | ---- | ----------------------------- |
| POST   | `/api/signup`       | No   | Create new user account       |
| POST   | `/api/login`        | No   | Authenticate user             |
| POST   | `/api/logout`       | No   | Clear session                 |
| GET    | `/api/csrf`         | No   | Get CSRF token                |
| GET    | `/api/me`           | Yes  | Get current user info         |
| POST   | `/api/webpage`      | Yes  | Add/update webpage monitoring |
| GET    | `/api/webpage`      | Yes  | List monitored webpages       |
| DELETE | `/api/webpage`      | Yes  | Stop monitoring a webpage     |
| GET    | `/api/image/{path}` | Yes  | Get optimized image           |
| GET    | `/health`           | No   | Health check endpoint         |

## Database Schema

```
User (extends AbstractUser)
├── username (6-18 chars, unique)
├── email
└── password (hashed)

Webpage
├── url (unique, max 2048 chars)
└── users → M2M through WebpageMonitoring

WebpageMonitoring
├── webpage → FK(Webpage)
├── user → FK(User)
├── interval ('minute' | 'hour' | 'day')
└── unique constraint on (webpage, user)

WebpageScreenshot
├── webpage → FK(Webpage, cascade delete)
├── perceptual_hash (64 chars)
└── created_at (auto timestamp)
```

## Security

- **Session-based authentication** with CSRF protection
- **Per-user data isolation** - Users only see their own monitored pages
- **Input validation** with Pydantic schemas
- **Password requirements** - 8-64 characters, common password check
- **Path validation** - Regex patterns prevent directory traversal
- **SSL/TLS termination** at Nginx gateway
- **Security headers** - X-Frame-Options, X-Content-Type-Options, etc.

## Code Quality

- **Type Safety** - MyPy with django-stubs and pydantic plugins
- **Linting** - Ruff for consistent code style
- **Formatting** - Single quotes, trailing commas, 100-char line length
- **Testing** - pytest for backend, Playwright for frontend E2E
- **CI Enforcement** - All checks must pass before merge
