#!/bin/bash
# read .env values
awk -F= '$1 == "BACKEND_DEBUG" {print $2}' .env
awk -F= '$1 == "BACKEND_PORT" {print $2}' .env
awk -F= '$1 == "CELERY_FLOWER_PORT" {print $2}' .env

echo "Running as: $RUN_TYPE"
cd backend/
if [ "$RUN_TYPE" = "web" ]; then
    python manage.py graph_models -o ../documentation/erd/app_models.png
    python manage.py spectacular --color --file schema.yml
    python manage.py migrate
    if [ ! -d "static" ]; then
        echo "Generating static files"
        python manage.py collectstatic --noinput
    fi
    if [ "$BACKEND_DEBUG" = 'True' ]; then   
        python manage.py runserver "0.0.0.0:${BACKEND_PORT:-8000}"
    else
        python -m granian --host 0.0.0.0 --port "${BACKEND_PORT:-8000}" --workers 8 --interface wsgi config.wsgi:application
    fi
elif [ "$RUN_TYPE" = "worker" ]; then
    celery -A config worker -l INFO -E --concurrency 1
elif [ "$RUN_TYPE" = "beat" ]; then
    sleep 15
    celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
elif [ "$RUN_TYPE" = "monitor" ]; then
    celery -A config flower --port="${CELERY_FLOWER_PORT:-5555}"
else
    echo "No RUN_TYPE value set. Exiting"
    exit 1
fi