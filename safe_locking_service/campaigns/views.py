from django.db.models import Max

from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from safe_locking_service.campaigns.serializers import CampaignSerializer
from safe_locking_service.locking_events.pagination import SmallPagination

from .models import Campaign


class CampaignsView(ListAPIView):
    """
    Returns a paginated list of campaigns.
    """

    pagination_class = SmallPagination
    serializer_class = CampaignSerializer

    def get_queryset(self):
        return (
            Campaign.objects.prefetch_related("activity_metadata")
            .annotate(last_updated=Max("periods__end_date"))
            .order_by("-start_date")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        paginated_data = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(paginated_data)


class RetrieveCampaignView(RetrieveAPIView):
    """
    Returns a campaign for the provided campaign_id.
    """

    serializer_class = CampaignSerializer

    def get_queryset(self, campaign_search_id: int):
        return (
            Campaign.objects.filter(campaign_search_id=campaign_search_id)
            .prefetch_related("activity_metadata")
            .annotate(last_updated=Max("periods__end_date"))
        )

    def get(self, request, *args, **kwargs):
        campaign_search_id = kwargs["campaign_search_id"]
        queryset = self.get_queryset(campaign_search_id)
        if not queryset:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(queryset[0])
        return Response(status=status.HTTP_200_OK, data=serializer.data)
