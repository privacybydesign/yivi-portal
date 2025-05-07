#!/bin/sh
export DJANGO_SETTINGS_MODULE=yivi_portal.settings.development

python manage.py migrate --noinput
poetry run python manage.py runserver 0.0.0.0:8000 --insecure
