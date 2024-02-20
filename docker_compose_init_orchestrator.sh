#!/bin/sh
# Script to initialize the local db and run the django server
echo "Migrating database (python3 manage.py migrate)"
python3 manage.py migrate
python3 manage.py spectacular --color --file /swagger/schema.yml --validate
python3 manage.py collectstatic --clear --noinput
echo "Initializing gunicorn..."
gunicorn --bind :8000 --workers 3 orchestrator.wsgi:application
