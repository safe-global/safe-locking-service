from django.urls import path

from . import views

app_name = "locking_events"

urlpatterns = [
    path("about/", views.AboutView.as_view(), name="about"),
    path("all-events/<str:address>/", views.AllEventsView.as_view(), name="all-events"),
]
