from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response

from gnosis.eth.utils import fast_is_checksum_address

from safe_locking_service import __version__
from safe_locking_service.locking_events.serializers import serialize_all_events
from safe_locking_service.locking_events.services.locking_service import LockingService
from safe_locking_service.pagination import SmallPagination


class AboutView(GenericAPIView):
    """
    Returns information and configuration of the service
    """

    @method_decorator(cache_page(5 * 60))  # 5 minutes
    def get(self, request, format=None):
        content = {
            "name": "Safe Locking Service",
            "version": __version__,
            "api_version": request.version,
            "secure": request.is_secure(),
            "host": request.get_host(),
            "headers": [x for x in request.META.keys() if "FORWARD" in x],
        }
        return Response(content)


class AllEventsView(ListAPIView):
    pagination_class = SmallPagination

    def get_queryset(self, address):
        return LockingService.get_all_events(holder=address)

    def list(self, request, *args, **kwargs):
        safe = self.kwargs["address"]
        queryset = self.get_queryset(safe)
        page = self.paginate_queryset(queryset)
        serialized_data = serialize_all_events(page)

        return self.get_paginated_response(serialized_data)

    def get(self, request, address, format=None):
        """
        Returns ether/tokens transfers for a Safe
        """
        if not fast_is_checksum_address(address):
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                data={
                    "code": 1,
                    "message": "Checksum address validation failed",
                    "arguments": [address],
                },
            )

        return super().get(request, address)
