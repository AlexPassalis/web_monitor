# Create a new django project: django-admin startproject <config folder name, e.g. config> .
# Create a new app inside the project: python manage.py startapp <app name, e.g. api>


# source .venv/bin/activate
.PHONY: install run

install:
	pip install -r requirements-dev.txt

run:
	uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --reload
