import logging

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection

logger = logging.getLogger(__name__)


def update_leaderboard_view():
    call_command("refresh_leaderboard_view")


MATERIALIZED_VIEW_TABLE_NAME = "campaign_leaderboards"


class Command(BaseCommand):
    help = "Refresh the leaderboard view for all campaigns"

    def handle(self, *args, **kwargs):
        """
        Refresh a materialized view which contains the ranking of all addresses for all campaigns.

        If the view needs to be created first, it is created with no data.
        The main reason for this is to avoid retrieved data and refreshing it right away (incurring in another retrieval).

        Refreshing the view is a step that is always executed.
        This action is idempotent, so given the same data, the materialized view will always be the same on re-execution.
        """
        with connection.cursor() as cursor:
            cursor.execute(f"REFRESH MATERIALIZED VIEW {MATERIALIZED_VIEW_TABLE_NAME};")
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully updated the view for the campaigns' leaderboards"
            )
        )
