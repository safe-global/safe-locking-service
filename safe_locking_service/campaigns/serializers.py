from rest_framework import serializers


class ActivitySerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    points = serializers.IntegerField()


class CampaignSerializer(serializers.Serializer):
    campaign_id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    last_updated = serializers.DateTimeField()
    activities = serializers.ListSerializer(child=ActivitySerializer())
