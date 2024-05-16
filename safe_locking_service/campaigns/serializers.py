from rest_framework import serializers

from safe_locking_service.campaigns.models import Activity, Campaign


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
    total_boost = serializers.DecimalField(max_digits=15, decimal_places=8)
    total_points = serializers.IntegerField()
    total_boosted_points = serializers.SerializerMethodField()

    def get_holder(self, obj: Activity):
        return obj["address"]

    def get_total_boosted_points(self, obj: Activity):
        return obj["total_campaign_boosted_points"]
