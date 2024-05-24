FROM python:3.11-slim

ARG APP_HOME=/app
WORKDIR ${APP_HOME}
ENV PYTHONUNBUFFERED=1

# https://eth-hash.readthedocs.io/en/latest/quickstart.html#specify-backend-by-environment-variable
# `pysha3` is way faster than `pycryptodome` for CPython
ENV ETH_HASH_BACKEND=pysha3

COPY requirements.txt ./
RUN set -ex \
	&& buildDeps=" \
		build-essential \
        git \
		libssl-dev \
        libpq-dev \
		" \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends $buildDeps tmux postgresql-client \
    && pip install -U --no-cache-dir wheel setuptools pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove $buildDeps \
    && rm -rf /var/lib/apt/lists/*

# /nginx mount point must be created before so it doesn't have root permissions
# ${APP_HOME} root folder will not be updated by COPY --chown, so permissions need to be adjusted
RUN groupadd -g 999 python && \
    useradd -u 999 -r -g python python && \
    mkdir -p /nginx && \
    chown -R python:python /nginx ${APP_HOME}
#COPY --chown=python:python . .
COPY --chown=python:python config config
COPY --chown=python:python manage.py manage.py
COPY --chown=python:python safe_locking_service safe_locking_service
COPY --chown=python:python docker/web/run_web.sh docker-entrypoint.sh
COPY --chown=python:python gunicorn.conf.py gunicorn.conf.py
COPY --chown=python:python gunicorn_custom_workers.py gunicorn_custom_workers.py

# Use numeric ids so kubernetes identifies the user correctly
USER 999:999

ENTRYPOINT ["./docker-entrypoint.sh"]
