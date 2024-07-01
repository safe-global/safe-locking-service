FROM python:3.11-slim as builder

# https://eth-hash.readthedocs.io/en/latest/quickstart.html#specify-backend-by-environment-variable
# `pysha3` is way faster than `pycryptodome` for CPython
ENV ETH_HASH_BACKEND=pysha3

COPY requirements.txt ./
RUN set -ex \
    && apt-get update \
    && apt-get install -y gcc libpq-dev \
    && pip install -U --no-cache-dir wheel setuptools pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*


# Production image
FROM python:3.11-slim

WORKDIR /app

# Force the stdout and stderr streams to be unbuffered. This option has no effect on the stdin stream.
# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUNBUFFERED
ENV PYTHONUNBUFFERED 1
ENV ETH_HASH_BACKEND=pysha3

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . /app/

# /nginx mount point must be created before so it doesn't have root permissions
# /app root folder will not be updated by COPY --chown, so permissions need to be adjusted
RUN groupadd -g 999 python && \
    useradd -u 999 -r -g python python && \
    mkdir -p /nginx && \
    chown -R python:python /nginx /app

RUN apt-get update \
    && apt-get install -y libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Use numeric ids so kubernetes identifies the user correctly
USER 999:999

RUN DJANGO_SETTINGS_MODULE=config.settings.production DJANGO_DOT_ENV_FILE=.env.docker python manage.py collectstatic --noinput
