from typing import Dict

from rest_framework import serializers

from gnosis.eth.django.serializers import EthereumAddressField
from gnosis.eth.utils import fast_to_checksum_address

from safe_locking_service.campaigns.models import Campaign


class ActivityMetadataSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    max_points = serializers.IntegerField()


class CampaignSerializer(serializers.Serializer):
    resource_id = serializers.SerializerMethodField()
    name = serializers.CharField()
    description = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    last_updated = serializers.SerializerMethodField()
    activities_metadata = ActivityMetadataSerializer(
        many=True, source="activity_metadata"
    )

    def get_resource_id(self, obj: Campaign):
        return obj.uuid

    def get_last_updated(self, obj: Campaign):
        return obj.last_updated


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
