from typing import Dict

from rest_framework import serializers

from gnosis.eth.django.serializers import EthereumAddressField
from gnosis.eth.utils import fast_to_checksum_address

from safe_locking_service.campaigns.models import Campaign, Partner


class ActivityMetadataSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    max_points = serializers.IntegerField()


class PartnerSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(use_url=True)

    class Meta:
        model = Partner
        fields = ["name", "logo"]


class CampaignSerializer(serializers.ModelSerializer):
    resource_id = serializers.UUIDField(source="uuid")
    last_updated = serializers.CharField()
    activities_metadata = ActivityMetadataSerializer(
        many=True, source="activity_metadata"
    )
    partners = PartnerSerializer(many=True, read_only=True)

    class Meta:
        model = Campaign
        fields = [
            "resource_id",
            "name",
            "description",
            "start_date",
            "end_date",
            "last_updated",
            "activities_metadata",
            "partners",
        ]


class CampaignLeaderBoardSerializer(serializers.Serializer):
    holder = serializers.SerializerMethodField()
    position = serializers.IntegerField()
    boost = serializers.SerializerMethodField()
    total_points = serializers.SerializerMethodField()
    total_boosted_points = serializers.SerializerMethodField()

    def get_holder(self, obj: Dict):
        if isinstance(obj["address"], str):
            return obj["address"]
        return fast_to_checksum_address(bytes(obj["address"]))

    def get_total_boosted_points(self, obj: Dict):
        return obj["total_campaign_boosted_points"]

    def get_boost(self, obj: Dict):
        return (
            obj["total_campaign_boosted_points"] / obj["total_campaign_points"]
            if obj["total_campaign_points"]
            else 0
        )

    def get_total_points(self, obj: Dict):
        return obj["total_campaign_points"]


class PeriodAddressSerializer(serializers.Serializer):
    start_date = serializers.DateField(source="period.start_date")
    end_date = serializers.DateField(source="period.end_date")
    holder = EthereumAddressField(source="address")
    boost = serializers.CharField()
    total_points = serializers.CharField()
    total_boosted_points = serializers.CharField()
