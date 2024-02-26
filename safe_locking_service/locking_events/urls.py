from django.urls import path

from . import views

app_name = "tokens"

urlpatterns = [
    path("about/", views.AboutView.as_view(), name="about"),
]
