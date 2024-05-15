from django.db import DataError, IntegrityError
from django.test import TestCase

from faker import Faker

from safe_locking_service.campaigns.tests.factories import CampaignFactory

fake = Faker(seed=0)


class CampaignsTestCase(TestCase):
    def test_campaign_creation(self):
        campaign = CampaignFactory.create()

        self.assertEqual(str(campaign), f"Campaign {campaign.uuid} {campaign.name}")

    def test_campaign_with_null_name(self):
        campaign = CampaignFactory.build(name=None)

        self.assertRaises(IntegrityError, campaign.save)

    def test_campaign_with_name_longer_than_50_characters(self):
        invalid_name = fake.pystr(min_chars=51, max_chars=255)
        campaign = CampaignFactory.build(name=invalid_name)

        self.assertRaises(DataError, campaign.save)

    def test_campaign_with_null_description(self):
        campaign = CampaignFactory.build(description=None)

        self.assertRaises(IntegrityError, campaign.save)

    def test_allows_null_start_date(self):
        campaign = CampaignFactory.build(start_date=None)

        campaign.save()

    def test_allows_null_end_date(self):
        campaign = CampaignFactory.build(end_date=None)

        campaign.save()
