#!/bin/bash
# rendre le script exécutable: chmod +x start.sh
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec gunicorn erp.wsgi:application --bind 0.0.0.0:$PORT