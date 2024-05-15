import uuid
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status

from ...campaigns.tests.factories import (
    ActivityMetadataFactory,
    CampaignFactory,
    PeriodFactory,
)
from ...utils.timestamp_helper import get_formated_timestamp


class TestCampaignViews(TestCase):
    def test_empty_campaigns_view(self):
        url = reverse("v1:locking_campaigns:list-campaigns")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # No campaigns
        response_json = response.json()
        self.assertEqual(response_json["count"], 0)

    def test_campaign_view(self):
        url = reverse("v1:locking_campaigns:list-campaigns")
        # Add campaign, one activity and 2 periods
        campaign_expected = CampaignFactory()
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
        self.assertEqual(
            campaign_response.get("campaignId"), str(campaign_expected.uuid)
        )
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
        self.assertEqual(len(campaign_response.get("activitiesMetadata")), 1)
        self.assertEqual(
            campaign_response.get("activitiesMetadata")[0]["name"], activity.name
        )

    def test_no_activities_periods_campaigns_view(self):
        # Add a campaign without activities and without period
        url = reverse("v1:locking_campaigns:list-campaigns")
        campaign_expected = CampaignFactory()
        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(len(response_json["results"]), 1)
        campaign_response = response_json["results"][0]
        self.assertEqual(
            campaign_response.get("campaignId"), str(campaign_expected.uuid)
        )
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
        self.assertIsInstance(campaign_response.get("activitiesMetadata"), list)
        self.assertEqual(len(campaign_response.get("activitiesMetadata")), 0)

    def test_sort_campaign_view(self):
        url = reverse("v1:locking_campaigns:list-campaigns")
        previous_day = timezone.now().date() - timedelta(days=1)
        CampaignFactory(start_date=previous_day, end_date=previous_day)
        # Last campaign should be at the beginning
        last_campaign = CampaignFactory()
        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(len(response_json["results"]), 2)
        campaign_response = response_json["results"][0]
        self.assertEqual(campaign_response.get("campaignId"), str(last_campaign.uuid))
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
        self.assertIsInstance(campaign_response.get("activitiesMetadata"), list)
        self.assertEqual(len(campaign_response.get("activitiesMetadata")), 0)

    def test_retrieve_campaign_view(self):
        campaign_id = uuid.uuid4()
        response = self.client.get(
            reverse("v1:locking_campaigns:retrieve-campaign", args=(campaign_id,)),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        campaign_expected = CampaignFactory()
        activity_expected = ActivityMetadataFactory(campaign=campaign_expected)
        period_expected = PeriodFactory(campaign=campaign_expected)
        campaign_id = campaign_expected.uuid

        response = self.client.get(
            reverse("v1:locking_campaigns:retrieve-campaign", args=(campaign_id,)),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        campaign_response = response.json()
        self.assertEqual(
            campaign_response.get("campaignId"), str(campaign_expected.uuid)
        )
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
        self.assertEqual(
            campaign_response.get("lastUpdated"),
            get_formated_timestamp(period_expected.end_date),
        )
        self.assertEqual(len(campaign_response.get("activitiesMetadata")), 1)
        self.assertEqual(
            campaign_response.get("activitiesMetadata")[0]["name"],
            activity_expected.name,
        )
