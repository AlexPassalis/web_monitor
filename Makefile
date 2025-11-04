# Create a new django project: django-admin startproject <config folder name, e.g. config> .
# Create a new app inside the project: python manage.py startapp <app name, e.g. api>

SHELL = /usr/bin/env bash -euo pipefail
MAKEFLAGS += --no-print-directory
LATESTDUMP = latest.dump

COMPOSE_NAME = project
BACKEND_SERVICE_NAME = backend

.PHONY: default init start stop lint fix check check_type test lint_backend fix_backend check_type_backend test_backend migrate create_superuser 

default: start

init:
	@echo "*** Initializing git hooks"
	git config core.hooksPath bin/.githooks

start:
	@if [ "$$(docker compose -p ${COMPOSE_NAME} ps -q 2>/dev/null | wc -l)" -eq 0 ]; then \
		bin/create_postgres_volume.sh; \
		bin/create_valkey_volume.sh; \
		bin/create_docker_network.sh; \
		docker compose -f docker-compose.yml up --build -d; \
	fi

stop:
	@if [ "$$(docker compose -p ${COMPOSE_NAME} ps -q 2>/dev/null | wc -l)" -eq 0 ]; then \
		echo "Docker compose \"${COMPOSE_NAME}\" is not running."; \
	else \
		docker compose -p ${COMPOSE_NAME} down; \
	fi

lint:
	@${MAKE} lint_backend

fix:
	@${MAKE} fix_backend

check:
	@${MAKE} lint
	@${MAKE} check_type

check_type:
	@${MAKE} check_type_backend

test:
	@${MAKE} test_backend

# BACKEND_SERVICE_NAME
lint_backend:
	@echo "*** Linting inside \"${BACKEND_SERVICE_NAME}\" service."
	@bin/dockerize_backend.sh ruff check .
	@bin/dockerize_backend.sh ruff format --check .

fix_backend:
	@echo "*** Linting and formatting inside \"${BACKEND_SERVICE_NAME}\" service."
	@bin/dockerize_backend.sh ruff format .
	@bin/dockerize_backend.sh ruff check --fix .

check_type_backend:
	@echo "*** Checking types inside \"${BACKEND_SERVICE_NAME}\" service."
	@bin/dockerize_backend.sh mypy .

test_backend:
	@echo "*** Running tests inside \"${BACKEND_SERVICE_NAME}\" service."
	@bin/dockerize_backend.sh env ENV=testing python -m pytest

migrate:
	@echo "*** Creating and applying database migrations."
	@bin/dockerize_backend.sh python manage.py makemigrations
	@bin/dockerize_backend.sh python manage.py migrate

create_superuser:
	@echo "*** Creating Django superuser."
	@bin/dockerize_backend.sh python manage.py createsuperuser
