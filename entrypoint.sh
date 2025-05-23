#!/bin/sh
export DJANGO_SETTINGS_MODULE=yivi_portal.settings.production

python manage.py migrate --noinput
python manage.py collectstatic --noinput
uwsgi --http :8000 --wsgi-file /app/yivi_portal/wsgi.py --master --processes 4 --threads 2 --uid nobody --gid nogroup --disable-logging --static-map ${STATIC_URL}=${STATIC_ROOT} --static-map ${MEDIA_URL}=${MEDIA_ROOT}
