#!/bin/bash
set -e

echo "Running as: $RUN_TYPE"
if [ "$RUN_TYPE" = "web" ]; then
    python backend/manage.py spectacular --color --file backend/schema.yml
    python backend/manage.py migrate
    if [ ! -d "backend/static" ]; then
        echo "Generating static files"
        python backend/manage.py collectstatic --noinput
    fi
    python backend/manage.py graph_models -o documentation/erd/app_models.png
    cd backend
    # python manage.py runserver 0.0.0.0:8000
    python -m gunicorn --bind 0.0.0.0:8000 -w 4 config.wsgi:application
elif [ "$RUN_TYPE" = "worker" ]; then
    cd backend && celery -A config worker -l INFO -E --concurrency 1
elif [ "$RUN_TYPE" = "beat" ]; then
    sleep 15
    cd backend && celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
elif [ "$RUN_TYPE" = "monitor" ]; then
    cd backend && celery -A config flower --port=5555
else
    echo "No RUN_TYPE value set. Defaulting to web mode"
    echo "No value specified, defaulting to web"
    python backend/manage.py spectacular --color --file backend/schema.yml
    python backend/manage.py migrate
    if [ ! -d "backend/static" ]; then
        echo "Generating static files"
        python backend/manage.py collectstatic --noinput
    fi
    python backend/manage.py graph_models -o documentation/erd/app_models.png
    cd backend
    # python manage.py runserver 0.0.0.0:8000
    python -m gunicorn --bind 0.0.0.0:8000 -w 4 config.wsgi:application
fi