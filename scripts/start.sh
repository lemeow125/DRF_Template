#!/bin/bash

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
        python manage.py runserver "0.0.0.0:8000"
    else
        gunicorn --workers 8 --bind 0.0.0.0:8000 config.wsgi:application # Gunicorn
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