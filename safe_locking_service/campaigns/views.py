from rest_framework.generics import ListAPIView

from safe_locking_service.campaigns.serializers import CampaignSerializer
from safe_locking_service.locking_events.pagination import SmallPagination

from .mock_data import mock_campaign_data


class CampaignsView(ListAPIView):
    """
    Returns a paginated list of campaigns.
    """

    pagination_class = SmallPagination
    serializer_class = CampaignSerializer

    def get_queryset(self):
        # TODO Add properly query
        # Mocking data for testing purposes
        return mock_campaign_data

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(data=queryset, many=True)
        serializer.is_valid(raise_exception=True)
        paginated_data = self.paginate_queryset(serializer.validated_data)
        return self.get_paginated_response(paginated_data)
