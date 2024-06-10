from django.urls import path

from . import views
from .views import GetAddressPeriodsView, upload_activities_view

app_name = "campaigns"

urlpatterns = [
    path("", views.CampaignsView.as_view(), name="list-campaigns"),
    path("upload/", upload_activities_view, name="activities_upload"),
    path(
        "<uuid:resource_id>/activities/",
        GetAddressPeriodsView.as_view(),
        name="get-address-periods",
    ),
    path(
        "<uuid:resource_id>/",
        views.RetrieveCampaignView.as_view(),
        name="retrieve-campaign",
    ),
    path(
        "<uuid:resource_id>/leaderboard/",
        views.CampaignLeaderBoardView.as_view(),
        name="leaderboard-campaign",
    ),
    path(
        "<uuid:resource_id>/leaderboard/<str:address>/",
        views.CampaignLeaderBoardPositionView.as_view(),
        name="leaderboard-campaign-position",
    ),
]
