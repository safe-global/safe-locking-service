import csv
import logging
from io import TextIOWrapper
from typing import IO

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import F, Max, Sum, Window
from django.db.models.functions import RowNumber
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from safe_locking_service.campaigns.serializers import (
    CampaignLeaderBoardSerializer,
    CampaignSerializer,
)
from safe_locking_service.locking_events.pagination import SmallPagination

from . import tasks
from .forms import FileUploadForm
from .models import Activity, Campaign, Period


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

    @method_decorator(cache_page(1 * 60))  # 1 minute
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

    def get_queryset(self, resource_id: int):
        return (
            Campaign.objects.filter(uuid=resource_id)
            .prefetch_related("activity_metadata")
            .annotate(last_updated=Max("periods__end_date"))
        )

    @method_decorator(cache_page(1 * 60))  # 1 minute
    def get(self, request, *args, **kwargs):
        resource_id = kwargs["resource_id"]
        queryset = self.get_queryset(resource_id)
        if not queryset:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(queryset[0])
        return Response(status=status.HTTP_200_OK, data=serializer.data)


csv_headers = {
    "safe_address",
    "period_start",
    "period_end",
    "total_points",
    "boost",
    "total_boosted_points",
    "points_rank",
    "boosted_points_rank",
}

logger = logging.getLogger(__name__)


@staff_member_required
def upload_activities_view(request) -> HttpResponse:
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                period = form.cleaned_data["period"]
                file = TextIOWrapper(
                    request.FILES["file"].file, encoding=request.encoding
                )
                process_activity_file(period, file)
                return redirect(reverse("admin:index"))
            except Exception as e:
                logger.warning(e)
                error_message = f"Invalid CSV format: {e}"
                return render(
                    request,
                    "activities/upload.html",
                    {"form": form, "error_message": error_message},
                )

    else:
        form = FileUploadForm()
    return render(request, "activities/upload.html", {"form": form})


def process_activity_file(period: Period, file: IO[str]) -> None:
    reader = csv.DictReader(file)

    file_headers = reader.fieldnames
    if not csv_headers.issubset(file_headers):
        raise ValueError(
            f"File does not include one or more of the following headers: {csv_headers}"
        )

    activities_list = [row for row in reader]
    tasks.process_csv_task.delay(period.id, activities_list)


class CampaignLeaderBoardView(ListAPIView):
    """
    Return the leaderboard for a provided campaign uuid
    """

    pagination_class = SmallPagination
    serializer_class = CampaignLeaderBoardSerializer

    def get_queryset(self, resource_id: int):
        return (
            Activity.objects.select_related("period__campaign")
            .filter(period__campaign__uuid=resource_id)
            .values("address")
            .annotate(
                total_campaign_points=Sum("total_points"),
                total_campaign_boosted_points=Sum("total_boosted_points"),
                last_boost=F("total_campaign_boosted_points")
                / F("total_campaign_points"),
            )
            .order_by(F("total_campaign_boosted_points").desc())
            .annotate(
                position=Window(
                    expression=RowNumber(),
                    order_by=F("total_campaign_boosted_points").desc(),
                )
            )
        )

    def list(self, request, *args, **kwargs):
        resource_id = kwargs["resource_id"]
        queryset = self.get_queryset(resource_id)
        serializer = self.serializer_class(queryset, many=True)
        paginated_data = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(paginated_data)
