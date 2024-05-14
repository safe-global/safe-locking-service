from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status

from safe_locking_service.campaigns.tests.factories import (
    ActivityMetadataFactory,
    CampaignFactory,
    PeriodFactory,
)
from safe_locking_service.utils.timestamp_helper import get_formated_timestamp


class TestCampaignViews(TestCase):
    def test_campaigns_view(self):
        url = reverse("v1:locking_campaigns:campaigns-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # No campaigns
        response_json = response.json()
        self.assertEqual(response_json["count"], 0)

        # Add a campaign without activities
        campaign_expected = CampaignFactory()
        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(len(response_json["results"]), 1)
        campaign_response = response_json["results"][0]
        self.assertEqual(campaign_response.get("campaignId"), campaign_expected.id)
        self.assertEqual(campaign_response.get("name"), campaign_expected.name)
        self.assertEqual(
            campaign_response.get("description"), campaign_expected.description
        )
        self.assertEqual(
            campaign_response.get("startDate"),
            get_formated_timestamp(campaign_expected.start_date),
        )
        self.assertEqual(
            campaign_response.get("endDate"),
            get_formated_timestamp(campaign_expected.end_date),
        )
        self.assertIsNone(campaign_response.get("lastUpdated"))
        self.assertIsInstance(campaign_response.get("activities"), list)
        self.assertEqual(len(campaign_response.get("activities")), 0)

        # Add an activity and 2 periods
        activity = ActivityMetadataFactory(campaign=campaign_expected)
        previous_day = timezone.now().date() - timedelta(days=1)
        PeriodFactory(
            campaign=campaign_expected, start_date=previous_day, end_date=previous_day
        )
        period_last = PeriodFactory(campaign=campaign_expected)
        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(len(response_json["results"]), 1)
        campaign_response = response_json["results"][0]
        self.assertEqual(campaign_response.get("campaignId"), campaign_expected.id)
        self.assertEqual(campaign_response.get("name"), campaign_expected.name)
        self.assertEqual(
            campaign_response.get("description"), campaign_expected.description
        )
        self.assertEqual(
            campaign_response.get("startDate"),
            get_formated_timestamp(campaign_expected.start_date),
        )
        self.assertEqual(
            campaign_response.get("endDate"),
            get_formated_timestamp(campaign_expected.end_date),
        )
        # LastUpdated should be the end_date of the last period
        self.assertEqual(
            campaign_response.get("lastUpdated"),
            get_formated_timestamp(period_last.end_date),
        )
        self.assertEqual(len(campaign_response.get("activities")), 1)
        self.assertEqual(campaign_response.get("activities")[0]["name"], activity.name)

        # Last campaign should be at the beginning
        last_campaign = CampaignFactory()
        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(len(response_json["results"]), 2)
        campaign_response = response_json["results"][0]
        self.assertEqual(campaign_response.get("campaignId"), last_campaign.id)
        self.assertEqual(campaign_response.get("name"), last_campaign.name)
        self.assertEqual(
            campaign_response.get("description"), last_campaign.description
        )
        self.assertEqual(
            campaign_response.get("startDate"),
            get_formated_timestamp(last_campaign.start_date),
        )
        self.assertEqual(
            campaign_response.get("endDate"),
            get_formated_timestamp(last_campaign.end_date),
        )
        self.assertIsNone(campaign_response.get("lastUpdated"))
        self.assertIsInstance(campaign_response.get("activities"), list)
        self.assertEqual(len(campaign_response.get("activities")), 0)
