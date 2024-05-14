from django.utils import timezone

from factory import Faker, LazyFunction, SubFactory
from factory.django import DjangoModelFactory

from ..models import ActivityMetadata, Campaign, Period


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


class ActivityMetadataFactory(DjangoModelFactory):
    class Meta:
        model = ActivityMetadata

    campaign = SubFactory(CampaignFactory)
    name = Faker("catch_phrase")
    description = Faker("bs")
    max_points = Faker("pyint")
