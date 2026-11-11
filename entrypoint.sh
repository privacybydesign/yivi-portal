#!/bin/sh
export DJANGO_SETTINGS_MODULE=yivi_portal.settings.production

python manage.py migrate --noinput
python manage.py collectstatic --noinput
# --buffer-size: uWSGI drops a request whose headers exceed its default of 4 KB, before Django
# sees it, so the client gets a 502 without CORS headers. The access token of a user in many
# organizations carries all their slugs and alone can come close to that limit.
uwsgi --http :8000 --wsgi-file /app/yivi_portal/wsgi.py --master --processes 4 --threads 2 --uid nobody --gid nogroup --disable-logging --buffer-size 32768 --static-map ${STATIC_URL}=${STATIC_ROOT} --static-map ${MEDIA_URL}=${MEDIA_ROOT}
