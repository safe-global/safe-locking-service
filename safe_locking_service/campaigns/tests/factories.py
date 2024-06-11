import random
from datetime import timedelta
from decimal import Decimal
from random import randrange

from django.utils import timezone
from django.utils.text import slugify

import factory
from eth_account import Account
from factory import Faker, LazyAttribute, LazyFunction, SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText

from ..models import Activity, ActivityMetadata, Campaign, Period


class CampaignFactory(DjangoModelFactory):
    class Meta:
        model = Campaign

    name = FuzzyText(length=randrange(51))
    description = Faker("bs")
    start_date = LazyFunction(timezone.now)
    end_date = LazyFunction(lambda: timezone.now() + timedelta(days=1))


class PeriodFactory(DjangoModelFactory):
    class Meta:
        model = Period

    campaign = SubFactory(CampaignFactory)
    start_date = LazyFunction(lambda: timezone.now().date())
    end_date = LazyFunction(lambda: timezone.now().date())
    slug = LazyAttribute(lambda p: slugify(f"{p.start_date}-{p.end_date}"))


def generate_random_decimal(
    min_value: int = 0, max_value: int = 1000, decimal_places: int = 2
) -> Decimal:
    value = Decimal(random.uniform(min_value, max_value))
    return round(value, decimal_places)


class ActivityFactory(DjangoModelFactory):
    class Meta:
        model = Activity

    period = SubFactory(PeriodFactory)
    address = LazyFunction(lambda: Account.create().address)
    total_points = Faker("pyint")

    @factory.lazy_attribute
    def boost(self):
        return generate_random_decimal(decimal_places=8)

    @factory.lazy_attribute
    def total_boosted_points(self):
        return generate_random_decimal(decimal_places=8)


class ActivityMetadataFactory(DjangoModelFactory):
    class Meta:
        model = ActivityMetadata

    campaign = SubFactory(CampaignFactory)
    name = Faker("catch_phrase")
    description = Faker("bs")
    max_points = Faker("pyint")
