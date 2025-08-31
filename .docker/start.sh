#!/bin/bash
# Startup script for Docker container

echo "Running as: $RUN_TYPE"
cd /app/src/
if [ "$RUN_TYPE" = "api" ]; then
    echo "Generating OpenAPI schema file"
    python manage.py spectacular --color --file schema.yml

    echo "Applying database migrations"
    python manage.py migrate

    if [ ! -d "static" ]; then
        echo "Generating static files"
        python manage.py collectstatic --noinput
    fi

    if [ "$BACKEND_DEBUG" = 'True' ]; then   
        python manage.py runserver "0.0.0.0:8000"
    else
        gunicorn --workers 8 --bind 0.0.0.0:8000 config.wsgi:application
    fi
# TODO: Add in other runtypes (i.e. Celery Worker, Beat, Flower, etc)
else
    echo "No RUN_TYPE value set. Exiting"
    exit 1
fi