from django.urls import path

from . import views

app_name = "campaigns"

urlpatterns = [
    path("campaigns/", views.CampaignsView.as_view(), name="campaigns-list"),
]
