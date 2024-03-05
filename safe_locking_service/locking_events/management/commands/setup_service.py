from dataclasses import dataclass
from typing import Tuple

from django.core.management.base import BaseCommand

from django_celery_beat.models import CrontabSchedule, IntervalSchedule, PeriodicTask


@dataclass
class CronDefinition:
    minute: str = "*"
    hour: str = "*"
    day_of_week: str = "*"
    day_of_month: str = "*"
    month_of_year: str = "*"


@dataclass
class CeleryTaskConfiguration:
    name: str
    description: str
    interval: int = 0
    period: str = None
    cron: CronDefinition = None
    enabled: bool = True

    def create_task(self) -> Tuple[PeriodicTask, bool]:
        assert self.period or self.cron, "Task must define period or cron"
        if self.period:
            interval_schedule, _ = IntervalSchedule.objects.get_or_create(
                every=self.interval, period=self.period
            )
            defaults = {
                "name": self.description,
                "interval": interval_schedule,
                "enabled": self.enabled,
            }
        else:
            crontab_schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=self.cron.minute,
                hour=self.cron.hour,
                day_of_week=self.cron.day_of_week,
                day_of_month=self.cron.day_of_month,
                month_of_year=self.cron.month_of_year,
            )
            defaults = {
                "name": self.description,
                "crontab": crontab_schedule,
                "enabled": self.enabled,
            }

        periodic_task, created = PeriodicTask.objects.get_or_create(
            task=self.name,
            defaults=defaults,
        )
        if not created:
            periodic_task.name = self.description
            if self.period:
                periodic_task.interval = interval_schedule
            else:
                periodic_task.crontab = crontab_schedule

            periodic_task.enabled = self.enabled
            periodic_task.save()

        return periodic_task, created


# List of tasks to be configured
TASKS = [
    CeleryTaskConfiguration(
        name="safe_locking_service.locking_events.tasks.index_locking_events_task",
        description="Index locking events (every 10 seconds)",
        interval=10,
        period=IntervalSchedule.SECONDS,
        enabled=True,
    ),
]


class Command(BaseCommand):
    help = "Setup Transaction Service Required Tasks"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Removing old tasks"))
        PeriodicTask.objects.filter(
            task__startswith="safe_transaction_service"
        ).delete()
        self.stdout.write(self.style.SUCCESS("Old tasks were removed"))

        for task in TASKS:
            _, created = task.create_task()
            if created:
                self.stdout.write(
                    self.style.SUCCESS("Created Periodic Task %s" % task.name)
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS("Task %s was already created" % task.name)
                )
