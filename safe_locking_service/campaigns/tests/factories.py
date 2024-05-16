from django.utils import timezone

from eth_account import Account
from factory import Faker, LazyFunction, SubFactory
from factory.django import DjangoModelFactory

from ..models import Activity, ActivityMetadata, Campaign, Period


class CampaignFactory(DjangoModelFactory):
    class Meta:
        model = Campaign

    name = Faker("catch_phrase")
    description = Faker("bs")
    start_date = LazyFunction(timezone.now)
    end_date = LazyFunction(timezone.now)


class PeriodFactory(DjangoModelFactory):
    class Meta:
        model = Period

    campaign = SubFactory(CampaignFactory)
    start_date = LazyFunction(lambda: timezone.now().date())
    end_date = LazyFunction(lambda: timezone.now().date())


class ActivityFactory(DjangoModelFactory):
    class Meta:
        model = Activity

    period = SubFactory(PeriodFactory)
    address = LazyFunction(lambda: Account.create().address)
    total_points = Faker("pyint")
    boost = Faker("pyint")
    total_boosted_points = Faker("pyint")


class ActivityMetadataFactory(DjangoModelFactory):
    class Meta:
        model = ActivityMetadata

    campaign = SubFactory(CampaignFactory)
    name = Faker("catch_phrase")
    description = Faker("bs")
    max_points = Faker("pyint")
