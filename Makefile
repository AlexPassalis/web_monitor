# Create a new django project: django-admin startproject <config folder name, e.g. config> .
# Create a new app inside the project: python manage.py startapp <app name, e.g. api>


# source .venv/bin/activate
.PHONY: run

run:
	python manage.py runserver
