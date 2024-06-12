from datetime import timedelta
from random import randrange

from django.utils import timezone
from django.utils.text import slugify

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


class ActivityFactory(DjangoModelFactory):
    class Meta:
        model = Activity

    period = SubFactory(PeriodFactory)
    address = LazyFunction(lambda: Account.create().address)
    total_points = Faker("pyint")
    boost = Faker("pydecimal", left_digits=7, right_digits=8, positive=True)
    total_boosted_points = Faker(
        "pydecimal", left_digits=7, right_digits=8, positive=True
    )


class ActivityMetadataFactory(DjangoModelFactory):
    class Meta:
        model = ActivityMetadata

    campaign = SubFactory(CampaignFactory)
    name = Faker("catch_phrase")
    description = Faker("bs")
    max_points = Faker("pyint")
