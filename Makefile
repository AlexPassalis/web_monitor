SHELL = /usr/bin/env bash -euo pipefail
MAKEFLAGS += --no-print-directory
LATESTDUMP = latest.dump

COMPOSE_NAME = project
FRONTEND_SERVICE_NAME = frontend
BACKEND_SERVICE_NAME = backend

.PHONY: default init start stop lint check_type check fix test install_backend lint_backend check_type_backend fix_backend test_backend migrate create_superuser 

default: start

init:
	@echo "*** Initializing git hooks"
	git config core.hooksPath bin/.githooks

start:
	@if [ "$$(docker compose -p ${COMPOSE_NAME} ps -q 2>/dev/null | wc -l)" -eq 0 ]; then \
		bin/create_postgres_volume; \
		bin/create_valkey_volume; \
		bin/create_docker_network; \
		${MAKE} install; \
		docker compose -f docker-compose.yml up --build -d; \
	fi

stop:
	@if [ "$$(docker compose -p ${COMPOSE_NAME} ps -q 2>/dev/null | wc -l)" -eq 0 ]; then \
		echo "Docker compose \"${COMPOSE_NAME}\" is not running."; \
	else \
		docker compose -p ${COMPOSE_NAME} down; \
	fi

install:
	@${MAKE} install_backend

lint:
	@${MAKE} lint_backend

check_type:
	@${MAKE} check_type_backend

check:
	@${MAKE} lint
	@${MAKE} check_type

fix:
	@${MAKE} fix_backend

test:
	@${MAKE} test_backend

# FRONTEND_SERVICE_NAME

# BACKEND_SERVICE_NAME
install_backend:
	@echo "*** Installing backend dependencies."
	@bin/create_venv
	@source .venv/bin/activate; \
		pip install --upgrade pip; \
		pip install -r services/backend/requirements/development.txt \

lint_backend:
	@echo "*** Linting inside \"${BACKEND_SERVICE_NAME}\" service."
	@bin/dockerize_backend ruff check .
	@bin/dockerize_backend ruff format --check .

check_type_backend:
	@echo "*** Checking types inside \"${BACKEND_SERVICE_NAME}\" service."
	@bin/dockerize_backend mypy .

fix_backend:
	@echo "*** Linting and formatting inside \"${BACKEND_SERVICE_NAME}\" service."
	@bin/dockerize_backend ruff format .
	@bin/dockerize_backend ruff check --fix .

test_backend:
	@echo "*** Running tests inside \"${BACKEND_SERVICE_NAME}\" service."
	@bin/dockerize_backend env ENV=testing python -m pytest

migrate:
	@echo "*** Creating and applying database migrations."
	@bin/dockerize_backend python manage.py makemigrations
	@bin/dockerize_backend python manage.py migrate

create_superuser:
	@echo "*** Creating Django superuser."
	@bin/dockerize_backend python manage.py createsuperuser
