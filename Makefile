# Create a new django project: django-admin startproject <config folder name, e.g. config> .
# Create a new app inside the project: python manage.py startapp <app name, e.g. api>

# source .venv/bin/activate

SHELL = /usr/bin/env bash -e -o pipefail
MAKEFLAGS += --no-print-directory
LATESTDUMP = "latest.dump"

.PHONY: create_docker_network install run 

default: run # Running 'make' without any additional arguments.

create_docker_network:
	@bin/create_docker_network.sh

install:
	pip install -r requirements-dev.txt

run:
	${MAKE} create_docker_network
	@exec uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --reload
