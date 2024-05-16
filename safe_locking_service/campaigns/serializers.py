from typing import Dict

from rest_framework import serializers

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
        return obj["address"]

    def get_total_boosted_points(self, obj: Dict):
        return obj["total_campaign_boosted_points"]

    def get_boost(self, obj: Dict):
        return obj["last_boost"]

    def get_total_points(self, obj: Dict):
        return obj["total_campaign_points"]
