# Create a new django project: django-admin startproject <config folder name, e.g. config> .
# Create a new app inside the project: python manage.py startapp <app name, e.g. api>

SHELL = /usr/bin/env bash -euo pipefail
MAKEFLAGS += --no-print-directory
LATESTDUMP = latest.dump

COMPOSE_NAME = project
BACKEND_SERVICE_NAME = backend

.PHONY: create_docker_network install start 

default: start

init:

start:
	@if [ "$$(docker compose -p ${COMPOSE_NAME} ps -q 2>/dev/null | wc -l)" -gt 0 ]; then \
		echo "Docker compose \"${COMPOSE_NAME}\" is already running."; \
	else \
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

check_type:
	@${MAKE} check_type_backend

test:
	@${MAKE} test_backend

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
