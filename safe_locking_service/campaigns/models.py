import uuid

from django.db import models
from django.utils.text import slugify

from gnosis.eth.django.models import EthereumAddressV2Field


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
        if not self.slug:
            self.slug = slugify(f"{self.start_date}-{self.end_date}")
        super(Period, self).save(*args, **kwargs)

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
