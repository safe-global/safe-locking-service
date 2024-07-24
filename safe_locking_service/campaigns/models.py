import os
import uuid
from decimal import Decimal
from typing import List, TypedDict

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db import connection, models
from django.db.backends.utils import CursorWrapper
from django.utils.text import slugify

from eth_typing import ChecksumAddress
from hexbytes import HexBytes

from gnosis.eth.django.models import EthereumAddressBinaryField


def get_campaign_icon_path(instance: "Campaign", filename):
    # file will be uploaded to MEDIA_ROOT/<address>
    _, extension = os.path.splitext(filename)
    return f"campaigns/icons/{instance.uuid}{extension}"  # extension includes '.'


def get_file_storage():
    if settings.AWS_S3_STORAGE_BACKEND_CONFIGURED:
        from django_s3_storage.storage import S3Storage

        return S3Storage()
    else:
        return default_storage


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
    reward_value = models.DecimalField(
        max_digits=15, decimal_places=8, null=True, blank=True
    )
    reward_text = models.CharField(null=True, blank=True)
    icon = models.ImageField(
        null=True,
        blank=True,
        default="",
        upload_to=get_campaign_icon_path,
        storage=get_file_storage,
    )
    safe_app_url = models.URLField(null=True, blank=True)
    partner_url = models.URLField(null=True, blank=True)
    is_promoted = models.BooleanField(default=False)
    visible = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Campaign, self).save()

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(
                {
                    "start_date": "Start date cannot be after end date",
                    "end_date": "End date cannot be before start date",
                }
            )

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
        if not self.slug:
            self.slug = slugify(f"{self.start_date}-{self.end_date}")
        self.full_clean()
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
        permissions = [
            ("upload_activities", "Can upload activities for the given period")
        ]

    def __str__(self):
        return f"{self.campaign} – Period {self.slug}"


class Activity(models.Model):
    period = models.ForeignKey(
        Period, on_delete=models.CASCADE, related_name="activities"
    )
    address = EthereumAddressBinaryField()
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
        verbose_name_plural = "Activities"

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
    SELECT * FROM campaign_leaderboards WHERE campaign_uuid=%s AND address=%s
    """

    with connection.cursor() as cursor:
        holder_address = HexBytes(address)
        cursor.execute(query, [uuid, holder_address])
        if result := fetch_all_from_cursor(cursor):
            return result[0]
