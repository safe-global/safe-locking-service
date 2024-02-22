from django.apps import AppConfig


class LockingEventsConfig(AppConfig):
    name = "safe_locking_service.locking_events"
    verbose_name = "Safe Locking Service"
    default_auto_field = "django.db.models.BigAutoField"
