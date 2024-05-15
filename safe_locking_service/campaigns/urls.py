from django.urls import path

from . import views

app_name = "campaigns"

urlpatterns = [
    path("campaigns/", views.CampaignsView.as_view(), name="list-campaigns"),
    path(
        "campaigns/<str:resource_id>/",
        views.RetrieveCampaignView.as_view(),
        name="retrieve-campaign",
    ),
]
