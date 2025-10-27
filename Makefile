# Create a new django project: django-admin startproject <config folder name, e.g. config> .
# Create a new app inside the project: python manage.py startapp <app name, e.g. api>

SHELL = /usr/bin/env bash -euo pipefail
MAKEFLAGS += --no-print-directory
LATESTDUMP = latest.dump

COMPOSE_NAME = project

.PHONY: create_docker_network install run 

default: run

init:

create_docker_network:
	@bin/create_docker_network.sh

create_postgres_volume:
	@bin/create_postgres_volume.sh

# pip_install:
# @${MAKE} dockerize_backend.sh
# pip install -r requirements-dev.txt

run:
	@${MAKE} create_docker_network
	@${MAKE} create_postgres_volume
	docker compose -f docker-compose.yml up --build -d

stop:
	docker compose -p ${COMPOSE_NAME} down
