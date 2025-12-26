SHELL = /usr/bin/env bash -euo pipefail
MAKEFLAGS += --no-print-directory
LATESTDUMP = latest.dump

COMPOSE_NAME = web_monitor
FRONTEND_SERVICE_NAME = frontend
BACKEND_SERVICE_NAME = backend

.PHONY: default init start stop install lint check_type check fix test install_frontend start_frontend stop_frontend lint_frontend check_type_frontend start_backend stop_backend install_backend lint_backend check_type_backend fix_backend test_backend test_coverage test_backend_coverage makemigrations migrate create_superuser 

default: start

init:
	@echo "==> Initializing git hooks"
	git config core.hooksPath bin/.githooks

start:
	@if [ "$$(docker compose -p ${COMPOSE_NAME} ps -q 2>/dev/null | wc -l)" -eq 0 ]; then \
		bin/create_postgres_volume; \
		bin/create_valkey_volume; \
		bin/create_minio_volume; \
		bin/create_docker_network; \
		${MAKE} start_backend; \
		${MAKE} start_frontend; \
	else \
		echo "Docker compose \"${COMPOSE_NAME}\" is already running."; \
	fi

stop:
	@if [ "$$(docker compose -p ${COMPOSE_NAME} ps -q 2>/dev/null | wc -l)" -eq 0 ]; then \
		echo "Docker compose \"${COMPOSE_NAME}\" is not running."; \
	else \
		${MAKE} stop_backend; \
		${MAKE} stop_frontend; \
	fi

install:
	@${MAKE} install_backend
	@${MAKE} install_frontend

lint:
	@${MAKE} lint_backend
	@${MAKE} lint_frontend

check_type:
	@${MAKE} check_type_backend
	@${MAKE} check_type_frontend

check:
	@${MAKE} lint
	@${MAKE} check_type

fix:
	@${MAKE} fix_backend

test:
	@${MAKE} test_backend

test_coverage:
	@${MAKE} test_backend_coverage

# BACKEND SERVICES
start_backend:
	@echo "==> Starting backend services"
	@docker compose -p ${COMPOSE_NAME} -f docker-compose.yml up -d

stop_backend:
	@echo "==> Stopping backend services"
	@docker compose -p ${COMPOSE_NAME} down

# FRONTEND
install_frontend:
	@echo "==> Installing frontend dependencies"
	@cd services/gateway/frontend && bun install

start_frontend:
	@echo "==> Starting \"${FRONTEND_SERVICE_NAME}\" service on host"
	@if [ "$${CI:-false}" != "true" ]; then \
		cd services/gateway/frontend && bun run dev; \
	else \
		cd services/gateway/frontend && bun run dev & \
	fi

stop_frontend:
	@echo "==> Stopping \"${FRONTEND_SERVICE_NAME}\" service on host"
	@pkill -f "bun run dev" || true

lint_frontend:
	@echo "==> Linting frontend on host"
	@cd services/gateway/frontend && bun run lint

check_type_frontend:
	@echo "==> Checking types in frontend on host"
	@cd services/gateway/frontend && bun run check

# BACKEND
install_backend:
	@echo "==> Installing backend dependencies"
	@cd services/backend && uv sync --extra dev

lint_backend:
	@echo "==> Linting inside \"${BACKEND_SERVICE_NAME}\" service"
	@if [ "$${CI:-false}" != "true" ]; then \
		bin/dockerize_backend uv run ruff check .; \
		bin/dockerize_backend uv run ruff format --check .; \
	else \
		bin/dockerize_backend uv run ruff check --no-cache .; \
		bin/dockerize_backend uv run ruff format --check --no-cache .; \
	fi

check_type_backend:
	@echo "==> Checking types inside \"${BACKEND_SERVICE_NAME}\" service"
	@bin/dockerize_backend uv run mypy .

fix_backend:
	@echo "==> Linting and formatting inside \"${BACKEND_SERVICE_NAME}\" service"
	@bin/dockerize_backend uv run ruff format .
	@bin/dockerize_backend uv run ruff check --fix .

test_backend:
	@echo "==> Running tests inside \"${BACKEND_SERVICE_NAME}\" service"
	@bin/dockerize_backend env ENV=testing uv run pytest

test_backend_coverage:
	@echo "==> Running tests with coverage inside \"${BACKEND_SERVICE_NAME}\" service"
	@if [ "$${CI:-false}" != "true" ]; then \
		bin/dockerize_backend env ENV=testing uv run pytest --cov --cov-branch --cov-report=xml --cov-report=html --cov-report=term-missing; \
	else \
		bin/dockerize_backend env ENV=testing uv run pytest --cov --cov-branch --cov-report=xml -p no:cacheprovider; \
	fi

makemigrations:
	@echo "==> Creating database migrations"
	@bin/dockerize_backend uv run python manage.py makemigrations

migrate:
	@echo "==> Applying database migrations"
	@bin/dockerize_backend uv run python manage.py migrate

check_missing_migrations:
	@echo "==> Checking for missing migrations"
	@bin/dockerize_backend uv run python manage.py makemigrations --check

create_superuser:
	@echo "==> Creating Django superuser"
	@bin/dockerize_backend uv run python manage.py createsuperuser

show_git_crypt:
	git-crypt status -e
