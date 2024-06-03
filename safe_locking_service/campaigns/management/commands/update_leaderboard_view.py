import logging

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection

logger = logging.getLogger(__name__)


def update_leaderboard_view():
    call_command("update_leaderboard_view")


MATERIALIZED_VIEW_TABLE_NAME = "campaign_leaderboards"

MATERIALIZED_VIEW_SQL = f"""
            CREATE MATERIALIZED VIEW IF NOT EXISTS {MATERIALIZED_VIEW_TABLE_NAME} AS
            SELECT "campaigns_activity"."address",
                   "campaigns_campaign"."uuid"                      AS "campaign_uuid",
                   SUM("campaigns_activity"."total_points")         AS "total_campaign_points",
                   SUM("campaigns_activity"."total_boosted_points") AS "total_campaign_boosted_points",
                   RANK() OVER (PARTITION BY "campaigns_campaign"."uuid" ORDER BY SUM("campaigns_activity"."total_boosted_points") DESC) AS "position"
            FROM "campaigns_activity"
                     INNER JOIN "campaigns_period" ON "campaigns_activity"."period_id" = "campaigns_period"."id"
                     INNER JOIN "campaigns_campaign" ON "campaigns_period"."campaign_id" = "campaigns_campaign"."id"
            GROUP BY "campaigns_activity"."address", "campaigns_campaign"."uuid"
            WITH NO DATA;

            CREATE UNIQUE INDEX IF NOT EXISTS leaderboard_address_position ON {MATERIALIZED_VIEW_TABLE_NAME} (address, campaign_uuid);

            REFRESH MATERIALIZED VIEW {MATERIALIZED_VIEW_TABLE_NAME};
"""


class Command(BaseCommand):
    help = "Update the leaderboard view for a campaign"

    def handle(self, *args, **kwargs):
        """
        Update a materialized view which contains the ranking of all addresses for all campaigns.

        If the view needs to be created first, it is created with no data.
        The main reason for this is to avoid retrieved data and refreshing it right away (incurring in another retrieval).

        Refreshing the view is a step that is always executed.
        This action is idempotent, so given the same data, the materialized view will always be the same on re-execution.
        """
        with connection.cursor() as cursor:
            cursor.execute(MATERIALIZED_VIEW_SQL)
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully updated the view for the campaigns' leaderboards"
            )
        )
