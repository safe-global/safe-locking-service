from django.urls import path

from . import views
from .views import upload_activities_view

app_name = "campaigns"

urlpatterns = [
    path("", views.CampaignsView.as_view(), name="list-campaigns"),
    path("upload/", upload_activities_view, name="activities_upload"),
    path(
        "<str:resource_id>/",
        views.RetrieveCampaignView.as_view(),
        name="retrieve-campaign",
    ),
]
