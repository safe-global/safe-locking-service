from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from faker import Faker

from safe_locking_service.campaigns.tests.factories import (
    CampaignFactory,
    PeriodFactory,
)

fake = Faker(seed=0)


class CampaignsTestCase(TestCase):
    def test_campaign_creation(self):
        campaign = CampaignFactory.create()

        self.assertEqual(str(campaign), f"Campaign {campaign.uuid} {campaign.name}")

    def test_campaign_with_null_name(self):
        with self.assertRaises(ValidationError):
            CampaignFactory(name=None)

    def test_campaign_with_name_longer_than_50_characters(self):
        invalid_name = fake.pystr(min_chars=51, max_chars=255)

        with self.assertRaises(ValidationError):
            CampaignFactory(name=invalid_name)

    def test_campaign_with_null_description(self):
        campaign = CampaignFactory.build(description=None)

        self.assertRaises(IntegrityError, campaign.save)

    def test_allows_null_start_date(self):
        campaign = CampaignFactory.build(start_date=None)

        campaign.save()

    def test_allows_null_end_date(self):
        campaign = CampaignFactory.build(end_date=None)

        campaign.save()

    def test_allows_same_dates(self):
        date = fake.date_time()

        CampaignFactory(end_date=date, start_date=date)

    def test_does_not_allow_end_date_before_start_date(self):
        start_date = fake.future_datetime()
        end_date = fake.past_datetime()

        with self.assertRaises(ValidationError):
            CampaignFactory(end_date=end_date, start_date=start_date)


class PeriodTestCase(TestCase):
    def test_allows_same_dates(self):
        date = fake.date()

        PeriodFactory(end_date=date, start_date=date)

    def test_does_not_allow_end_date_before_start_date(self):
        start_date = fake.future_date()
        end_date = fake.past_date()

        period = PeriodFactory.build(end_date=end_date, start_date=start_date)

        with self.assertRaises(ValidationError):
            period.save()
