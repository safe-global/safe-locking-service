from rest_framework import serializers

from safe_locking_service.campaigns.models import Campaign


class ActivityMetadataSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    max_points = serializers.IntegerField()


class CampaignSerializer(serializers.Serializer):
    campaign_id = serializers.SerializerMethodField()
    name = serializers.CharField()
    description = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    last_updated = serializers.SerializerMethodField()
    activities_metadata = ActivityMetadataSerializer(
        many=True, source="activity_metadata"
    )

    def get_campaign_id(self, obj: Campaign):
        return obj.uuid

    def get_last_updated(self, obj: Campaign):
        return obj.last_updated
