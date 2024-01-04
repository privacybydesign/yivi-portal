#!/bin/sh
python manage.py migrate --noinput
uwsgi --http :8000 --wsgi-file /app/yivi_portal/wsgi.py --master --processes 4 --threads 2 --uid nobody --gid nogroup --static-map ${DJANGO_STATIC_URL}=${DJANGO_STATIC_ROOT} --static-map ${DJANGO_MEDIA_URL}=${DJANGO_MEDIA_ROOT}