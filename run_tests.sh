#!/bin/bash

set -euo pipefail

export DJANGO_SETTINGS_MODULE=config.settings.test
export DJANGO_DOT_ENV_FILE=.env.test
docker compose -f docker-compose.yml -f docker-compose.dev.yml build --force-rm db ganache rabbitmq
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --no-start db ganache rabbitmq
docker compose -f docker-compose.yml -f docker-compose.dev.yml start db ganache rabbitmq

sleep 10

python manage.py check
pytest -rxXs
