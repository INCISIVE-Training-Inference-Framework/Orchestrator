#!/bin/sh
# Script to initialize the local db and run the django server
echo "Migrating database (python3 manage.py migrate)"
python3 manage.py migrate
echo "Initializing gunicorn..."
gunicorn --bind :8000 --workers 3 orchestrator.wsgi:application
