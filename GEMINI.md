# Project Overview

This is a full-stack web application with a Django/Python backend and a React/TypeScript frontend. The backend provides an API for the frontend and uses Celery for asynchronous tasks, including taking screenshots of web pages with Playwright and comparing them with ImageHash. The application is containerized with Docker and managed with a `Makefile`.

## Project Structure

```
.
├── bin/                    # Scripts for managing the project
├── services/
│   ├── app/
│   │   ├── backend/        # Django backend
│   │   └── frontend/       # React frontend
│   ├── cache/              # Valkey (Redis fork) service
│   ├── db/                 # PostgreSQL service
│   └── gateway/            # Nginx gateway (not yet implemented)
├── docker-compose.yml      # Docker compose file
├── Makefile                # Makefile with commands for managing the project
└── README.md               # Project README
```

## Technologies

**Backend:**
- Python 3.13
- Django 5.2
- Django Ninja
- Celery
- PostgreSQL
- Valkey (Redis fork)
- Playwright
- ImageHash
- Pillow
- `uv` for package management

**Frontend:**
- React 19
- TypeScript
- Tailwind CSS
- `bun` for package management

**Infrastructure:**
- Docker
- docker-compose
- MinIO (S3-compatible storage)

## Building and Running

The project is managed with a `Makefile`. Here are the most common commands:

- **`make start`**: Start the application in detached mode. This will also create the necessary Docker volumes and networks if they don't exist.
- **`make stop`**: Stop the application.
- **`make install`**: Install all frontend and backend dependencies.
- **`make lint`**: Lint the frontend and backend code.
- **`make check_type`**: Type-check the frontend and backend code.
- **`make test`**: Run the backend tests.
- **`make migrate`**: Create and apply database migrations.
- **`make create_superuser`**: Create a Django superuser.
- **`make build_frontend`**: Build the frontend for production and copy the assets to the backend's static directory.

## Development Conventions

- The backend code is formatted with `ruff format` and linted with `ruff check`.
- The backend code is type-checked with `mypy`.
- The frontend code is managed with `bun`.
- The project follows the conventional commit specification for commit messages.
- The project uses `pre-commit` and `pre-push` git hooks to enforce code quality. To install the hooks, run `make init`.

## How to Contribute

1.  **Fork the repository.**
2.  **Create a new branch.**
3.  **Make your changes.**
4.  **Make sure the tests pass.** (`make test`)
5.  **Make sure the code is linted and formatted correctly.** (`make lint` and `make fix`)
6.  **Commit your changes.**
7.  **Push your changes to your fork.**
8.  **Create a pull request.**
