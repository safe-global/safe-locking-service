from datetime import datetime

from django.test import TestCase
from django.urls import reverse

from rest_framework import status


class TestCampaignViews(TestCase):
    def test_campaigns_view(self):
        url = reverse("v1:locking_campaigns:campaigns-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test that return correct types
        response_json = response.json()
        self.assertEqual(response_json["count"], 2)
        self.assertEqual(len(response_json["results"]), 2)
        campaign_1 = response_json["results"][0]
        self.assertIsInstance(campaign_1.get("campaignId"), str)
        self.assertIsInstance(campaign_1.get("name"), str)
        self.assertIsInstance(campaign_1.get("description"), str)
        period_start_datetime = datetime.strptime(
            campaign_1.get("periodStart"), "%Y-%m-%dT%H:%M:%SZ"
        )
        self.assertIsInstance(period_start_datetime, datetime)
        period_end_datetime = datetime.strptime(
            campaign_1.get("periodEnd"), "%Y-%m-%dT%H:%M:%SZ"
        )
        self.assertIsInstance(period_end_datetime, datetime)
        last_updated_datetime = datetime.strptime(
            campaign_1.get("lastUpdated"), "%Y-%m-%dT%H:%M:%SZ"
        )
        self.assertIsInstance(last_updated_datetime, datetime)
        self.assertIsInstance(campaign_1.get("activities"), list)
