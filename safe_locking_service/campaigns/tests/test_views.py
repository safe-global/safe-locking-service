import uuid
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from eth_account import Account
from faker import Faker
from rest_framework import status

from ...campaigns.tests.factories import (
    ActivityFactory,
    ActivityMetadataFactory,
    CampaignFactory,
)
from ...utils.timestamp_helper import get_formated_timestamp
from ..forms import FileUploadForm
from ..management.commands.refresh_leaderboard_view import update_leaderboard_view
from ..models import Period
from .csv_factory import CSVFactory
from .factories import PeriodFactory

fake = Faker(0)


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
            campaign_response.get("resourceId"), str(campaign_expected.uuid)
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

    def test_campaign_order_view(self):
        url = reverse("v1:locking_campaigns:list-campaigns")

        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        before_yesterday = today - timedelta(days=2)

        # sorted in descending order by start time and end time
        first_campaign_expected = CampaignFactory(start_date=yesterday, end_date=today)
        second_campaign_expected = CampaignFactory(
            start_date=before_yesterday, end_date=today
        )
        third_campaign_expected = CampaignFactory(
            start_date=before_yesterday, end_date=yesterday
        )

        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(len(response_json["results"]), 3)
        first_campaign_response = response_json["results"][0]
        self.assertEqual(
            first_campaign_response.get("resourceId"), str(first_campaign_expected.uuid)
        )
        second_campaign_response = response_json["results"][1]
        self.assertEqual(
            second_campaign_response.get("resourceId"),
            str(second_campaign_expected.uuid),
        )
        third_campaign_response = response_json["results"][2]
        self.assertEqual(
            third_campaign_response.get("resourceId"), str(third_campaign_expected.uuid)
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
            campaign_response.get("resourceId"), str(campaign_expected.uuid)
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
        self.assertEqual(campaign_response.get("resourceId"), str(last_campaign.uuid))
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
        resource_id = uuid.uuid4()
        response = self.client.get(
            reverse("v1:locking_campaigns:retrieve-campaign", args=(resource_id,)),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        campaign_expected = CampaignFactory()
        activity_expected = ActivityMetadataFactory(campaign=campaign_expected)
        period_expected = PeriodFactory(campaign=campaign_expected)
        resource_id = campaign_expected.uuid

        response = self.client.get(
            reverse("v1:locking_campaigns:retrieve-campaign", args=(resource_id,)),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        campaign_response = response.json()
        self.assertEqual(
            campaign_response.get("resourceId"), str(campaign_expected.uuid)
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

    def test_hidden_campaigns_view(self):
        url = reverse("v1:locking_campaigns:list-campaigns")
        # Add campaign, one activity and one period
        campaign_expected = CampaignFactory()
        ActivityMetadataFactory(campaign=campaign_expected)
        PeriodFactory(campaign=campaign_expected)

        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(len(response_json["results"]), 1)

        # Add hidden campaign, one activity and one period
        campaign_hidden_expected = CampaignFactory(visible=False)
        ActivityMetadataFactory(campaign=campaign_hidden_expected)
        PeriodFactory(campaign=campaign_hidden_expected)
        response = self.client.get(url, format="json")
        response_json = response.json()
        self.assertEqual(len(response_json["results"]), 1)

    def test_retrieve_hidden_campaign_view(self):
        campaign_hidden_expected = CampaignFactory(visible=False)
        resource_hidden_id = campaign_hidden_expected.uuid

        response = self.client.get(
            reverse(
                "v1:locking_campaigns:retrieve-campaign", args=(resource_hidden_id,)
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestActivitiesUploadView(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a normal user
        self.user = User.objects.create_user("user", "user@example.com", "userpass")
        # Allow the User to login (staff)
        self.user.is_staff = True
        self.user.save()
        # Add permission to upload activities for this user
        content_type = ContentType.objects.get_for_model(Period)
        permission = Permission.objects.get(
            codename="upload_activities", content_type=content_type
        )
        self.user.user_permissions.add(permission)
        self.client.login(username="user", password="userpass")
        self.period = PeriodFactory()

    @patch("safe_locking_service.campaigns.tasks.process_csv_task.delay")
    def test_form_retrieval(self, task_mock):
        response = self.client.get(reverse("v1:campaigns:activities_upload"))

        task_mock.assert_not_called()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "activities/upload.html")
        self.assertIsInstance(response.context["form"], FileUploadForm)

    @patch("safe_locking_service.campaigns.tasks.process_csv_task.delay")
    def test_valid_activities_upload(self, task_mock):
        csv_content = CSVFactory().create()
        upload = SimpleUploadedFile(
            "testfile.csv", csv_content.encode("utf-8"), content_type="text/csv"
        )

        response = self.client.post(
            reverse("v1:campaigns:activities_upload"),
            {"file": upload, "period": self.period.id},
        )

        task_mock.assert_called_once()
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse("admin:index"))

    @patch("safe_locking_service.campaigns.tasks.process_csv_task.delay")
    def test_empty_data_upload(self, task_mock):
        response = self.client.get(reverse("v1:campaigns:activities_upload"), {})

        task_mock.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertTrue("form" in response.context)
        self.assertFalse(response.context["form"].is_valid())

    @patch("safe_locking_service.campaigns.tasks.process_csv_task.delay")
    def test_wrong_header(self, task_mock):
        address = "0x146f5Eb4313030Aa052C68a21072c8744F60E6B4"
        points = fake.pyint()
        type = fake.word()
        csv_content = (
            f"{fake.word()},{fake.word()},{fake.word()}\n{address},{points},{type}"
        )
        upload = SimpleUploadedFile(
            "testfile.csv", csv_content.encode("utf-8"), content_type="text/csv"
        )

        response = self.client.post(
            reverse("v1:campaigns:activities_upload"),
            {"file": upload, "period": self.period.id},
        )

        task_mock.assert_not_called()
        self.assertEqual(200, response.status_code)
        self.assertTrue(
            response.context.get("error_message").startswith(
                "Error processing CSV: File does not include one or more of the following headers:"
            )
        )

    def test_empty_leaderboard_campaigns_view(self):
        resource_id = str(CampaignFactory().uuid)
        response = self.client.get(
            reverse("v1:locking_campaigns:leaderboard-campaign", args=(resource_id,)),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # No campaigns
        response_json = response.json()
        self.assertEqual(response_json["count"], 0)

    def test_leaderboard_campaigns_view(self):
        campaign = CampaignFactory()
        previous_day = timezone.now().date() - timedelta(days=1)
        period_1 = PeriodFactory(
            campaign=campaign, start_date=previous_day, end_date=previous_day
        )
        period_2 = PeriodFactory(campaign=campaign)
        safe_address_position_1 = Account.create().address
        safe_address_position_2 = Account.create().address
        ActivityFactory(
            period=period_1,
            address=safe_address_position_1,
            total_points=100,
            boost=2,
            total_boosted_points=200,
        )
        ActivityFactory(
            period=period_1,
            address=safe_address_position_2,
            total_points=100,
            boost=1,
            total_boosted_points=100,
        )
        ActivityFactory(
            period=period_2,
            address=safe_address_position_1,
            total_points=100,
            boost=2,
            total_boosted_points=200,
        )
        ActivityFactory(
            period=period_2,
            address=safe_address_position_2,
            total_points=100,
            boost=1,
            total_boosted_points=100,
        )

        resource_id = campaign.uuid
        response = self.client.get(
            reverse("v1:locking_campaigns:leaderboard-campaign", args=(resource_id,)),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # No campaigns
        response_json = response.json()
        self.assertEqual(response_json["count"], 2)

        position_1 = response_json["results"][0]
        self.assertEqual(position_1["holder"], safe_address_position_1)
        self.assertEqual(position_1["position"], 1)
        self.assertEqual(position_1["totalPoints"], 200)
        self.assertEqual(position_1["boost"], 2)
        self.assertEqual(position_1["totalBoostedPoints"], 400)

        position_2 = response_json["results"][1]
        self.assertEqual(position_2["holder"], safe_address_position_2)
        self.assertEqual(position_2["position"], 2)
        self.assertEqual(position_2["totalPoints"], 200)
        self.assertEqual(position_2["boost"], 1)
        self.assertEqual(position_2["totalBoostedPoints"], 200)

        # Should pass position 2 to 1
        next_day = timezone.now().date() + timedelta(days=1)
        period_3 = PeriodFactory(
            campaign=campaign, start_date=next_day, end_date=next_day
        )
        ActivityFactory(
            period=period_3,
            address=safe_address_position_2,
            total_points=200,
            boost=2,
            total_boosted_points=400,
        )
        response = self.client.get(
            reverse("v1:locking_campaigns:leaderboard-campaign", args=(resource_id,)),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual(response_json["count"], 2)
        first_position = response_json["results"][0]
        self.assertEqual(first_position["holder"], safe_address_position_2)
        self.assertEqual(first_position["position"], 1)
        self.assertEqual(first_position["totalPoints"], 400)
        self.assertEqual(first_position["boost"], 1.5)
        self.assertEqual(first_position["totalBoostedPoints"], 600)

    def test_rank_of_leaderboard_campaigns_view(self):
        campaign = CampaignFactory()
        period_1 = PeriodFactory(campaign=campaign)
        # Because will have the same totalBoostedPoints will be ordered by address.
        safe_address_position_1 = "0x71E4B15483d3FFd1099C0284799Ce7b1dcd1563d"
        safe_address_other_position_1 = "0xE05f244ddEC210b2789f34292Aa5335f934683B2"
        safe_address_position_3 = Account.create().address
        ActivityFactory(
            period=period_1,
            address=safe_address_position_1,
            total_points=200,
            boost=1,
            total_boosted_points=200,
        )
        ActivityFactory(
            period=period_1,
            address=safe_address_other_position_1,
            total_points=200,
            boost=1,
            total_boosted_points=200,
        )
        ActivityFactory(
            period=period_1,
            address=safe_address_position_3,
            total_points=50,
            boost=1,
            total_boosted_points=50,
        )

        resource_id = campaign.uuid
        response = self.client.get(
            reverse("v1:locking_campaigns:leaderboard-campaign", args=(resource_id,)),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # No campaigns
        response_json = response.json()
        self.assertEqual(response_json["count"], 3)

        position_1 = response_json["results"][0]
        self.assertEqual(position_1["holder"], safe_address_position_1)
        self.assertEqual(position_1["position"], 1)
        self.assertEqual(position_1["totalPoints"], 200)
        self.assertEqual(position_1["boost"], 1)
        self.assertEqual(position_1["totalBoostedPoints"], 200)

        other_position_1 = response_json["results"][1]
        self.assertEqual(other_position_1["holder"], safe_address_other_position_1)
        self.assertEqual(other_position_1["position"], 1)
        self.assertEqual(other_position_1["totalPoints"], 200)
        self.assertEqual(other_position_1["boost"], 1)
        self.assertEqual(other_position_1["totalBoostedPoints"], 200)

        position_3 = response_json["results"][2]
        self.assertEqual(position_3["holder"], safe_address_position_3)
        self.assertEqual(position_3["position"], 3)
        self.assertEqual(position_3["totalPoints"], 50)
        self.assertEqual(position_3["boost"], 1)
        self.assertEqual(position_3["totalBoostedPoints"], 50)

    def test_rank_of_leaderboard_hidden_campaign_view(self):
        campaign = CampaignFactory(visible=False)
        period_1 = PeriodFactory(campaign=campaign)
        safe_address_position_1 = "0x71E4B15483d3FFd1099C0284799Ce7b1dcd1563d"
        ActivityFactory(
            period=period_1,
            address=safe_address_position_1,
            total_points=200,
            boost=1,
            total_boosted_points=200,
        )

        resource_id = campaign.uuid
        response = self.client.get(
            reverse("v1:locking_campaigns:leaderboard-campaign", args=(resource_id,)),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_leaderboard_campaign_position_view(self):
        # Should return 404 error
        response = self.client.get(
            reverse(
                "v1:locking_campaigns:leaderboard-campaign-position",
                args=(uuid.uuid4(), Account.create().address),
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        campaign = CampaignFactory()
        previous_day = timezone.now().date() - timedelta(days=1)
        period_1 = PeriodFactory(
            campaign=campaign, start_date=previous_day, end_date=previous_day
        )
        period_2 = PeriodFactory(campaign=campaign)
        safe_address_position_1 = Account.create().address
        safe_address_position_2 = Account.create().address

        ActivityFactory(
            period=period_1,
            address=safe_address_position_1,
            total_points=100,
            boost=2,
            total_boosted_points=200,
        )
        ActivityFactory(
            period=period_1,
            address=safe_address_position_2,
            total_points=100,
            boost=1,
            total_boosted_points=100,
        )
        ActivityFactory(
            period=period_2,
            address=safe_address_position_1,
            total_points=100,
            boost=2,
            total_boosted_points=200,
        )
        ActivityFactory(
            period=period_2,
            address=safe_address_position_2,
            total_points=100,
            boost=1,
            total_boosted_points=100,
        )
        resource_id = campaign.uuid
        # Refresh materialized view
        update_leaderboard_view()

        response = self.client.get(
            reverse(
                "v1:locking_campaigns:leaderboard-campaign-position",
                args=(resource_id, safe_address_position_1),
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        position_1 = response.json()
        self.assertEqual(position_1["holder"], safe_address_position_1)
        self.assertEqual(position_1["position"], 1)
        self.assertEqual(position_1["totalPoints"], 200)
        self.assertEqual(position_1["boost"], 2)
        self.assertEqual(position_1["totalBoostedPoints"], 400)
        response = self.client.get(
            reverse(
                "v1:locking_campaigns:leaderboard-campaign-position",
                args=(resource_id, safe_address_position_2),
            ),
            format="json",
        )
        position_2 = response.json()
        self.assertEqual(position_2["holder"], safe_address_position_2)
        self.assertEqual(position_2["position"], 2)
        self.assertEqual(position_2["totalPoints"], 200)
        self.assertEqual(position_2["boost"], 1)
        self.assertEqual(position_2["totalBoostedPoints"], 200)

    def test_leaderboard_hidden_campaign_position_view(self):
        campaign = CampaignFactory(visible=False)
        previous_day = timezone.now().date() - timedelta(days=1)
        period_1 = PeriodFactory(
            campaign=campaign, start_date=previous_day, end_date=previous_day
        )
        safe_address_position_1 = Account.create().address
        safe_address_position_2 = Account.create().address

        ActivityFactory(
            period=period_1,
            address=safe_address_position_1,
            total_points=100,
            boost=2,
            total_boosted_points=200,
        )
        ActivityFactory(
            period=period_1,
            address=safe_address_position_2,
            total_points=100,
            boost=1,
            total_boosted_points=100,
        )
        resource_id = campaign.uuid
        # Refresh materialized view
        update_leaderboard_view()

        response = self.client.get(
            reverse(
                "v1:locking_campaigns:leaderboard-campaign-position",
                args=(resource_id, safe_address_position_1),
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rank_of_leaderboard_campaign_position_view(self):
        # Test that we are using rank
        safe_address_position_1 = Account.create().address
        safe_address_other_position_1 = Account.create().address
        safe_address_position_3 = Account.create().address
        campaign = CampaignFactory()
        resource_id = campaign.uuid
        period_1 = PeriodFactory(campaign=campaign)
        ActivityFactory(
            period=period_1,
            address=safe_address_position_1,
            total_points=200,
            boost=1,
            total_boosted_points=200,
        )
        ActivityFactory(
            period=period_1,
            address=safe_address_other_position_1,
            total_points=200,
            boost=1,
            total_boosted_points=200,
        )
        ActivityFactory(
            period=period_1,
            address=safe_address_position_3,
            total_points=50,
            boost=1,
            total_boosted_points=50,
        )
        # Refresh materialized view
        update_leaderboard_view()

        response = self.client.get(
            reverse(
                "v1:locking_campaigns:leaderboard-campaign-position",
                args=(resource_id, safe_address_position_1),
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        position_1 = response.json()
        self.assertEqual(position_1["holder"], safe_address_position_1)
        self.assertEqual(position_1["position"], 1)
        self.assertEqual(position_1["totalPoints"], 200)
        self.assertEqual(position_1["boost"], 1)
        self.assertEqual(position_1["totalBoostedPoints"], 200)

        response = self.client.get(
            reverse(
                "v1:locking_campaigns:leaderboard-campaign-position",
                args=(resource_id, safe_address_other_position_1),
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        position_1 = response.json()
        self.assertEqual(position_1["holder"], safe_address_other_position_1)
        self.assertEqual(position_1["position"], 1)
        self.assertEqual(position_1["totalPoints"], 200)
        self.assertEqual(position_1["boost"], 1)
        self.assertEqual(position_1["totalBoostedPoints"], 200)

        response = self.client.get(
            reverse(
                "v1:locking_campaigns:leaderboard-campaign-position",
                args=(resource_id, safe_address_position_3),
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        position_1 = response.json()
        self.assertEqual(position_1["holder"], safe_address_position_3)
        self.assertEqual(position_1["position"], 3)
        self.assertEqual(position_1["totalPoints"], 50)
        self.assertEqual(position_1["boost"], 1)
        self.assertEqual(position_1["totalBoostedPoints"], 50)


class TestActivitiesUploadViewNoPermissions(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a normal user
        self.user = User.objects.create_user("user", "user@example.com", "userpass")
        # Allow the User to login (staff)
        self.user.is_staff = True
        self.user.save()
        self.client.login(username="user", password="userpass")
        self.period = PeriodFactory()

    @patch("safe_locking_service.campaigns.tasks.process_csv_task.delay")
    def test_form_retrieval_returns_403(self, task_mock):
        response = self.client.get(reverse("v1:campaigns:activities_upload"))

        task_mock.assert_not_called()
        self.assertEqual(403, response.status_code)

    @patch("safe_locking_service.campaigns.tasks.process_csv_task.delay")
    def test_valid_activities_upload_returns_403(self, task_mock):
        csv_content = CSVFactory().create()
        upload = SimpleUploadedFile(
            "testfile.csv", csv_content.encode("utf-8"), content_type="text/csv"
        )

        response = self.client.post(
            reverse("v1:campaigns:activities_upload"),
            {"file": upload, "period": self.period.id},
        )

        task_mock.assert_not_called()
        self.assertEqual(403, response.status_code)


class TestGetAddressPeriodsView(TestCase):
    def test_empty_periods_view(self):
        campaign = CampaignFactory.create()
        holder = Account.create().address

        response = self.client.get(
            reverse("v1:locking_campaigns:get-address-periods", args=[campaign.uuid]),
            {"holder": holder},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(), {"count": 0, "next": None, "previous": None, "results": []}
        )

    def test_non_existent_campaign_uuid(self):
        campaign = CampaignFactory.build()
        holder = Account.create().address

        response = self.client.get(
            reverse("v1:locking_campaigns:get-address-periods", args=[campaign.uuid]),
            {"holder": holder},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_periods_are_returned_correctly(self):
        holder = Account.create().address
        campaign = CampaignFactory()
        period_1 = PeriodFactory(
            campaign=campaign, start_date="2024-06-11", end_date="2024-06-12"
        )
        period_2 = PeriodFactory(
            campaign=campaign, start_date="2024-06-12", end_date="2024-06-13"
        )
        period_3 = PeriodFactory(
            campaign=campaign, start_date="2024-06-13", end_date="2024-06-14"
        )
        activity_1 = ActivityFactory(period=period_1, address=holder)
        activity_2 = ActivityFactory(period=period_2, address=holder)
        activity_3 = ActivityFactory(period=period_3, address=holder)

        response = self.client.get(
            reverse(
                "v1:locking_campaigns:get-address-periods",
                kwargs={"resource_id": campaign.uuid},
            ),
            {"holder": holder},
            format="json",
        )

        json_response = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["count"], 3)
        self.assertListEqual(
            json_response["results"],
            [
                {
                    "boost": str(activity_3.boost),
                    "endDate": str(period_3.end_date),
                    "holder": holder,
                    "startDate": str(period_3.start_date),
                    "totalBoostedPoints": str(activity_3.total_boosted_points),
                    "totalPoints": str(activity_3.total_points),
                },
                {
                    "boost": str(activity_2.boost),
                    "endDate": str(period_2.end_date),
                    "holder": holder,
                    "startDate": str(period_2.start_date),
                    "totalBoostedPoints": str(activity_2.total_boosted_points),
                    "totalPoints": str(activity_2.total_points),
                },
                {
                    "boost": str(activity_1.boost),
                    "endDate": str(period_1.end_date),
                    "holder": holder,
                    "startDate": str(period_1.start_date),
                    "totalBoostedPoints": str(activity_1.total_boosted_points),
                    "totalPoints": str(activity_1.total_points),
                },
            ],
        )

    def test_periods_for_a_different_campaign_are_not_returned(self):
        holder = Account.create().address
        # Activity for Campaign 1
        campaign_1 = CampaignFactory()
        period_1 = PeriodFactory(
            campaign=campaign_1, start_date="2024-06-11", end_date="2024-06-12"
        )
        activity_1 = ActivityFactory(period=period_1, address=holder)
        # Activity for Campaign 2
        campaign_2 = CampaignFactory()
        period_2 = PeriodFactory(
            campaign=campaign_2, start_date="2024-06-12", end_date="2024-06-13"
        )
        ActivityFactory(period=period_2, address=holder)

        response = self.client.get(
            reverse(
                "v1:locking_campaigns:get-address-periods",
                kwargs={"resource_id": campaign_1.uuid},
            ),
            {"holder": holder},
            format="json",
        )

        json_response = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["count"], 1)
        self.assertListEqual(
            json_response["results"],
            [
                {
                    "boost": str(activity_1.boost),
                    "endDate": str(period_1.end_date),
                    "startDate": str(period_1.start_date),
                    "holder": holder,
                    "totalBoostedPoints": str(activity_1.total_boosted_points),
                    "totalPoints": str(activity_1.total_points),
                },
            ],
        )

    def test_periods_for_a_different_addresses_are_not_returned(self):
        holder_1 = Account.create().address
        holder_2 = Account.create().address
        campaign = CampaignFactory()
        period = PeriodFactory(
            campaign=campaign, start_date="2024-06-11", end_date="2024-06-12"
        )
        activity_1 = ActivityFactory(period=period, address=holder_1)
        # Activity tied to Address 2
        ActivityFactory(period=period, address=holder_2)

        response = self.client.get(
            reverse(
                "v1:locking_campaigns:get-address-periods",
                kwargs={"resource_id": campaign.uuid},
            ),
            {"holder": holder_1},
            format="json",
        )

        json_response = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["count"], 1)
        self.assertListEqual(
            json_response["results"],
            [
                {
                    "boost": str(activity_1.boost),
                    "endDate": str(period.end_date),
                    "startDate": str(period.start_date),
                    "holder": holder_1,
                    "totalBoostedPoints": str(activity_1.total_boosted_points),
                    "totalPoints": str(activity_1.total_points),
                },
            ],
        )

    def test_periods_for_a_different_addresses_are_returned(self):
        address_1 = Account.create().address
        address_2 = Account.create().address
        campaign = CampaignFactory()
        period = PeriodFactory(
            campaign=campaign, start_date="2024-06-11", end_date="2024-06-12"
        )
        activity_1 = ActivityFactory(period=period, address=address_1)
        # Activity tied to Address 2
        activity_2 = ActivityFactory(period=period, address=address_2)

        response = self.client.get(
            reverse(
                "v1:locking_campaigns:get-address-periods",
                kwargs={"resource_id": campaign.uuid},
            ),
            format="json",
        )

        json_response = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["count"], 2)
        self.assertCountEqual(
            json_response["results"],
            [
                {
                    "boost": str(activity_1.boost),
                    "endDate": str(period.end_date),
                    "startDate": str(period.start_date),
                    "holder": address_1,
                    "totalBoostedPoints": str(activity_1.total_boosted_points),
                    "totalPoints": str(activity_1.total_points),
                },
                {
                    "boost": str(activity_2.boost),
                    "endDate": str(period.end_date),
                    "startDate": str(period.start_date),
                    "holder": address_2,
                    "totalBoostedPoints": str(activity_2.total_boosted_points),
                    "totalPoints": str(activity_2.total_points),
                },
            ],
        )

    def test_periods_for_hidden_campaign_are_not_returned(self):
        holder = Account.create().address
        campaign = CampaignFactory(visible=False)
        period = PeriodFactory(
            campaign=campaign, start_date="2024-06-11", end_date="2024-06-12"
        )
        ActivityFactory(period=period, address=holder)

        response = self.client.get(
            reverse(
                "v1:locking_campaigns:get-address-periods",
                kwargs={"resource_id": campaign.uuid},
            ),
            {"holder": holder},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
