from django.urls import path

from . import views

app_name = "locking_events"

urlpatterns = [
    path("about/", views.AboutView.as_view(), name="about"),
    path("all-events/<str:address>/", views.AllEventsView.as_view(), name="all-events"),
    path("leaderboard/", views.LeaderBoardView.as_view(), name="leaderboard"),
    path(
        "leaderboard/<str:address>/",
        views.LeaderBoardPositionView.as_view(),
        name="leaderboard",
    ),
    path(
        "lock-events/<str:address>/", views.LockEventsView.as_view(), name="lock-events"
    ),
]
