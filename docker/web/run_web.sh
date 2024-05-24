#!/bin/bash

set -euo pipefail

DOCKER_SHARED_DIR=/nginx

echo "==> $(date +%H:%M:%S) ==> Collecting statics... "
python manage.py collectstatic --noinput
rm -rf $DOCKER_SHARED_DIR/*
cp -r staticfiles/ $DOCKER_SHARED_DIR/

echo "==> $(date +%H:%M:%S) ==> Migrating Django models..."
python manage.py migrate --noinput

echo "==> $(date +%H:%M:%S) ==> Running Gunicorn... "
exec gunicorn --config gunicorn.conf.py --pythonpath "$PWD" -b unix:$DOCKER_SHARED_DIR/gunicorn.socket -b 0.0.0.0:8888 config.wsgi:application
