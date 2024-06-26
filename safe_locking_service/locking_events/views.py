from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from gnosis.eth.utils import fast_is_checksum_address

from safe_locking_service import __version__
from safe_locking_service.locking_events.models import (
    LockEvent,
    UnlockEvent,
    WithdrawnEvent,
    get_leader_board,
    get_leader_board_count,
    get_leader_board_holder_position,
)
from safe_locking_service.locking_events.pagination import (
    CustomListPagination,
    SmallPagination,
)
from safe_locking_service.locking_events.serializers import (
    AboutSerializer,
    AllEventsDocSerializer,
    LeaderBoardSerializer,
    LockEventSerializer,
    UnlockOrWithdrawnEventSerializer,
    serialize_all_events,
)
from safe_locking_service.locking_events.services.locking_service import LockingService


class AboutView(GenericAPIView):
    """
    Returns information and configuration of the service
    """

    serializer_class = AboutSerializer

    def get_queryset(self):
        return {
            "name": "Safe Locking Service",
            "version": __version__,
            "api_version": self.request.version,
            "secure": self.request.is_secure(),
            "host": self.request.get_host(),
            "headers": [x for x in self.request.META.keys() if "FORWARD" in x],
        }

    @method_decorator(cache_page(5 * 60))  # 5 minutes
    def get(self, request, format=None):
        serializer = self.serializer_class(data=self.get_queryset())
        serializer.is_valid()
        return Response(serializer.data)


class AllEventsView(ListAPIView):
    """
    Returns a paginated list of last events executed by the provided address.
    """

    pagination_class = SmallPagination
    serializer_class = AllEventsDocSerializer  # Just for documentation

    def get_queryset(self, address):
        locking_service = LockingService(address)
        return locking_service.get_all_events_by_holder()

    def list(self, request, *args, **kwargs):
        safe = self.kwargs["address"]
        queryset = self.get_queryset(safe)
        page_queryset = self.paginate_queryset(queryset)
        serialized_data = serialize_all_events(page_queryset)
        response = self.get_paginated_response(serialized_data)
        return response

    def get(self, request, address, format=None):
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


class LeaderBoardView(ListAPIView):
    """
    Returns the leaderboard ordered by `lockedAmount`.
    """

    pagination_class = SmallPagination  # Just for documentation
    serializer_class = LeaderBoardSerializer

    def get_queryset(self, limit, offset):
        return get_leader_board(limit=limit, offset=offset)

    def list(self, request, *args, **kwargs):
        paginator = CustomListPagination(self.request)
        queryset = self.get_queryset(paginator.limit, paginator.offset)
        paginator.set_count(get_leader_board_count())
        serializer = LeaderBoardSerializer(queryset, many=True)

        return paginator.get_paginated_response(serializer.data)

    def get(self, request, format=None):
        return super().get(request)


class LeaderBoardPositionView(RetrieveAPIView):
    """
    Returns the leaderboard data for a provided address.
    """

    serializer_class = LeaderBoardSerializer

    def get_queryset(self, address):
        return get_leader_board_holder_position(address)

    def get(self, request, address, format=None):
        if not fast_is_checksum_address(address):
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                data={
                    "code": 1,
                    "message": "Checksum address validation failed",
                    "arguments": [address],
                },
            )
        queryset = self.get_queryset(address)
        if not queryset:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LeaderBoardSerializer(queryset)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class LockEventsView(ListAPIView):
    """
    Returns a paginated list of last lock events executed by the provided address.
    """

    pagination_class = SmallPagination
    serializer_class = LockEventSerializer

    def get_queryset(self):
        holder = self.kwargs["address"]
        return LockEvent.objects.filter(holder=holder).order_by("-timestamp")

    def get(self, request, address, format=None):
        address = self.kwargs["address"]
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


class UnlockEventsView(ListAPIView):
    """
    Returns a paginated list of last unlock events executed by the provided address.
    """

    pagination_class = SmallPagination
    serializer_class = UnlockOrWithdrawnEventSerializer

    def get_queryset(self):
        holder = self.kwargs["address"]
        return UnlockEvent.objects.filter(holder=holder).order_by("-timestamp")

    def get(self, request, address, format=None):
        address = self.kwargs["address"]
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


class WithdrawEventsView(ListAPIView):
    """
    Returns a paginated list of last withdrawn events executed by the provided address.
    """

    pagination_class = SmallPagination
    serializer_class = UnlockOrWithdrawnEventSerializer

    def get_queryset(self):
        holder = self.kwargs["address"]
        return WithdrawnEvent.objects.filter(holder=holder).order_by("-timestamp")

    def get(self, request, address, format=None):
        address = self.kwargs["address"]
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
