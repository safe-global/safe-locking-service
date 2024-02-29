"""
Base settings to build other settings files upon.
"""

from pathlib import Path

import environ
from corsheaders.defaults import default_headers as default_cors_headers

from ..gunicorn import (
    gunicorn_request_timeout,
    gunicorn_worker_connections,
    gunicorn_workers,
)

ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
APPS_DIR = ROOT_DIR / "safe_locking_service"

env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
DOT_ENV_FILE = env("DJANGO_DOT_ENV_FILE", default=None)
if READ_DOT_ENV_FILE or DOT_ENV_FILE:
    DOT_ENV_FILE = DOT_ENV_FILE or ".env"
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR / DOT_ENV_FILE))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DEBUG", False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "UTC"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# https://docs.djangoproject.com/en/3.2/ref/settings/#force-script-name
FORCE_SCRIPT_NAME = env("FORCE_SCRIPT_NAME", default=None)

# GUNICORN
GUNICORN_REQUEST_TIMEOUT = gunicorn_request_timeout
GUNICORN_WORKER_CONNECTIONS = gunicorn_worker_connections
GUNICORN_WORKERS = gunicorn_workers

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DB_STATEMENT_TIMEOUT = env.int("DB_STATEMENT_TIMEOUT", 60_000)
DATABASES = {
    "default": env.db("DATABASE_URL"),
}
DATABASES["default"]["ATOMIC_REQUESTS"] = False
DATABASES["default"]["ENGINE"] = "django_db_geventpool.backends.postgresql_psycopg2"
DATABASES["default"]["CONN_MAX_AGE"] = 0
DB_MAX_CONNS = env.int("DB_MAX_CONNS", default=50)
DATABASES["default"]["OPTIONS"] = {
    # https://github.com/jneight/django-db-geventpool#settings
    "MAX_CONNS": DB_MAX_CONNS,
    "REUSE_CONNS": env.int("DB_REUSE_CONNS", default=DB_MAX_CONNS),
    "options": f"-c statement_timeout={DB_STATEMENT_TIMEOUT}",
}

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 'django.contrib.humanize', # Handy template tags
]
THIRD_PARTY_APPS = [
    "django_extensions",
    "corsheaders",
    "rest_framework",
    "drf_yasg",
]
LOCAL_APPS = [
    "safe_locking_service.locking_events.apps.LockingEventsConfig",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "safe_locking_service.utils.loggers.LoggingMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR / "staticfiles")

# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [
    str(APPS_DIR / "static"),
]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR / "media")
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "DIRS": [
            str(APPS_DIR / "templates"),
        ],
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            "debug": DEBUG,
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# CORS
# ------------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = list(default_cors_headers) + [
    "if-match",
    "if-modified-since",
    "if-none-match",
]
CORS_EXPOSE_HEADERS = ["etag"]

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),)

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL regex.
ADMIN_URL = "admin/"

# Celery
# ------------------------------------------------------------------------------
INSTALLED_APPS += [
    "django_celery_beat",
]

# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_url
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="django://")
# https://docs.celeryproject.org/en/stable/userguide/optimizing.html#broker-connection-pools
# https://docs.celeryq.dev/en/latest/userguide/optimizing.html#broker-connection-pools
# Configured to 0 due to connection issues https://github.com/celery/celery/issues/4355
CELERY_BROKER_POOL_LIMIT = env.int("CELERY_BROKER_POOL_LIMIT", default=0)
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#broker-heartbeat
CELERY_BROKER_HEARTBEAT = env.int("CELERY_BROKER_HEARTBEAT", default=0)

# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-broker_connection_max_retries
CELERY_BROKER_CONNECTION_MAX_RETRIES = env.int(
    "CELERY_BROKER_CONNECTION_MAX_RETRIES", default=0
)
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#broker-channel-error-retry
CELERY_BROKER_CHANNEL_ERROR_RETRY = env.bool(
    "CELERY_BROKER_CHANNEL_ERROR_RETRY", default=True
)
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_backend
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://")
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-accept_content
CELERY_ACCEPT_CONTENT = ["json"]
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_serializer
CELERY_TASK_SERIALIZER = "json"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_serializer
CELERY_RESULT_SERIALIZER = "json"
# We are not interested in keeping results of tasks
CELERY_IGNORE_RESULT = True
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_always_eager
CELERY_ALWAYS_EAGER = False
# https://docs.celeryproject.org/en/latest/userguide/configuration.html#task-default-priority
# Higher = more priority on RabbitMQ, opposite on Redis ¯\_(ツ)_/¯
CELERY_TASK_DEFAULT_PRIORITY = 5
# https://docs.celeryproject.org/en/stable/userguide/configuration.html#task-queue-max-priority
CELERY_TASK_QUEUE_MAX_PRIORITY = 10
# https://docs.celeryproject.org/en/latest/userguide/configuration.html#broker-transport-options
CELERY_BROKER_TRANSPORT_OPTIONS = {}

# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-task_routes
# CELERY_ROUTES = (
#    [
#        (
#            "safe_locking_service.locking_events.tasks.*",
#            {"queue": "events", "delivery_mode": "transient"},
#        ),
#    ])

# Django REST Framework
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "PAGE_SIZE": 10,
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_RENDERER_CLASSES": (
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # 'rest_framework.authentication.BasicAuthentication',
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    # TODO Check this
    "EXCEPTION_HANDLER": "safe_locking_service.utils.exceptions.custom_exception_handler",
}

# LOGGING
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins bon every HTTP 500 error when DEBUG=False.
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "ignore_succeeded_none": {
            "()": "safe_locking_service.utils.loggers.IgnoreSucceededNone"
        },
    },
    "formatters": {
        "short": {"format": "%(asctime)s %(message)s"},
        "verbose": {
            "format": "%(asctime)s [%(levelname)s] [%(processName)s] %(message)s"
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "console_short": {
            "class": "logging.StreamHandler",
            "formatter": "short",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "web3.providers": {
            "level": "DEBUG" if DEBUG else "WARNING",
        },
        "django.geventpool": {
            "level": "DEBUG" if DEBUG else "WARNING",
        },
        "LoggingMiddleware": {
            "handlers": ["console_short"],
            "level": "INFO",
            "propagate": False,
        },
        "safe_locking_service": {
            "level": "DEBUG" if DEBUG else "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console", "mail_admins"],
            "propagate": True,
        },
    },
}

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "api_key": {"type": "apiKey", "in": "header", "name": "Authorization"}
    },
}

REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")

# Ethereum
ETHEREUM_NODE_URL = env("ETHEREUM_NODE_URL", default=None)

# Event indexing
SAFE_LOCKING_CONTRACT_ADDRESS = env("SAFE_LOCKING_CONTRACT_ADDRESS", default=None)
ETH_EVENTS_BLOCK_PROCESS_LIMIT = env.int(
    "ETH_EVENTS_BLOCK_PROCESS_LIMIT", default=50
)  # Initial number of blocks to process together when searching for events. It will be auto increased. 0 == no limit.
ETH_EVENTS_BLOCK_PROCESS_LIMIT_MAX = env.int(
    "ETH_EVENTS_BLOCK_PROCESS_LIMIT_MAX", default=0
)  # Maximum number of blocks to process together when searching for events. 0 == no limit.
ETH_EVENTS_BLOCKS_TO_REINDEX_AGAIN = env.int(
    "ETH_EVENTS_BLOCKS_TO_REINDEX_AGAIN", default=2
)  # Blocks to reindex again every indexer run when service is synced. Useful for RPCs not reliable
ETH_EVENTS_GET_LOGS_CONCURRENCY = env.int(
    "ETH_EVENTS_GET_LOGS_CONCURRENCY", default=20
)  # Number of concurrent requests to `getLogs`
ETH_EVENTS_UPDATED_BLOCK_BEHIND = env.int(
    "ETH_EVENTS_UPDATED_BLOCK_BEHIND", default=24 * 60 * 60 // 15
)  # Number of blocks to consider an address 'almost updated'.
