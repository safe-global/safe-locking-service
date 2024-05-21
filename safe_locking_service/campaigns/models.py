import uuid
from decimal import Decimal
from typing import List, TypedDict

from django.core.exceptions import ValidationError
from django.db import connection, models
from django.db.backends.utils import CursorWrapper
from django.utils.text import slugify

from eth_typing import ChecksumAddress
from hexbytes import HexBytes

from gnosis.eth.django.models import EthereumAddressV2Field


class LeaderBoardCampaignRow(TypedDict):
    address: ChecksumAddress
    total_campaign_points: int
    total_campaign_boosted_points: Decimal
    position: int


def fetch_all_from_cursor(cursor: CursorWrapper) -> List[LeaderBoardCampaignRow]:
    """

    :param cursor:
    :return: all rows from a db cursor as a List of `LeaderBoardCampaignRow`.
    """
    columns = [col[0] for col in cursor.description]

    return [dict(zip(columns, row)) for row in cursor.fetchall()]


class Campaign(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    name = models.CharField(max_length=50)
    description = models.CharField(blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Campaign {self.uuid} {self.name}"


class Period(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="periods"
    )
    slug = models.SlugField()
    start_date = models.DateField()
    end_date = models.DateField()

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.slug:
            self.slug = slugify(f"{self.start_date}-{self.end_date}")
        super(Period, self).save(*args, **kwargs)

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError(
                {
                    "start_date": "Start date cannot be after end date",
                    "end_date": "End date cannot be before start date",
                }
            )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["campaign", "end_date"], name="unique_period"
            )
        ]

    def __str__(self):
        return f"{self.campaign} – Period {self.slug}"


class Activity(models.Model):
    period = models.ForeignKey(
        Period, on_delete=models.CASCADE, related_name="activities"
    )
    address = EthereumAddressV2Field()
    total_points = models.PositiveBigIntegerField()
    boost = models.DecimalField(max_digits=15, decimal_places=8)
    total_boosted_points = models.DecimalField(max_digits=15, decimal_places=8)

    # TODO List of activity types

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["period", "address"], name="unique_activity"
            )
        ]

    def __str__(self):
        return f"Activity {self.period} {self.address}"


class ActivityMetadata(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="activity_metadata"
    )
    name = models.CharField(max_length=50)
    description = models.CharField(blank=True)
    max_points = models.PositiveBigIntegerField()


def get_campaign_leader_board_position(
    uuid: str, address: ChecksumAddress
) -> LeaderBoardCampaignRow:
    """

    :return: a Dict of LeaderBoardCampaignRow
    """

    query = """
    Select * FROM
    (SELECT "campaigns_activity"."address",
       SUM("campaigns_activity"."total_points") AS "total_campaign_points",
       SUM("campaigns_activity"."total_boosted_points") AS "total_campaign_boosted_points",
       ROW_NUMBER() OVER (ORDER BY SUM("campaigns_activity"."total_boosted_points") DESC) AS "position"
    FROM "campaigns_activity"
    INNER JOIN "campaigns_period"
    ON ("campaigns_activity"."period_id" = "campaigns_period"."id")
    INNER JOIN "campaigns_campaign"
    ON ("campaigns_period"."campaign_id" = "campaigns_campaign"."id")
    WHERE "campaigns_campaign"."uuid" = %s::uuid
    GROUP BY "campaigns_activity"."address"
    ORDER BY "total_campaign_boosted_points" DESC) AS LEADERTABLE where address = %s;
    """

    with connection.cursor() as cursor:
        holder_address = HexBytes(address)
        cursor.execute(query, [uuid, holder_address])
        if result := fetch_all_from_cursor(cursor):
            return result[0]
