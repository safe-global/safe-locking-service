import factory
from factory.django import DjangoModelFactory

from ..models import Campaign


class CampaignFactory(DjangoModelFactory):
    class Meta:
        model = Campaign

    name = factory.Faker("catch_phrase")
    description = factory.Faker("bs")
    start_date = factory.Faker("date_time")
    end_date = factory.Faker("date_time")
