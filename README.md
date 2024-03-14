[![Python CI](https://github.com/safe-global/safe-locking-service/actions/workflows/python.yml/badge.svg?branch=main)](https://github.com/safe-global/safe-locking-service/actions/workflows/python.yml)
[![Coverage Status](https://coveralls.io/repos/github/safe-global/safe-locking-service/badge.svg?branch=main)](https://coveralls.io/github/safe-global/safe-locking-service?branch=main)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)
![Django 5](https://img.shields.io/badge/Django-5-blue.svg)
[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/safeglobal/safe-locking-service?label=Docker&sort=semver)](https://hub.docker.com/r/safeglobal/safe-locking-service)

# Safe Locking Service

Keeps track emitted events by Safe token locking contract. https://github.com/safe-global/safe-locking

## Configuration
```bash
cp .env.sample .env
```

Configure environment variables on `.env`:

- `DJANGO_SECRET_KEY`: **IMPORTANT: Update it with a secure generated string**.
- `ETHEREUM_NODE_URL`: RPC node url.

## Execution

```bash
docker compose build
docker compose up
```

Then go to http://localhost:8000 to see the service documentation.

## Endpoints
- /v1/about

## Setup for development
Use a virtualenv if possible:

```bash
python -m venv venv
```

Then enter the virtualenv and install the dependencies:

```bash
source venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install -f
cp .env.sample .env
./run_tests.sh
```

## Contributors
[See contributors](https://github.com/safe-global/safe-locking-service/graphs/contributors)
