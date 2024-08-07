from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, re_path
from django.views import defaults as default_views

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Safe Locking Service API",
        default_version="v1",
        description="Get events emitted by Safe token locking contract.",
        license=openapi.License(name="MIT License"),
    ),
    validators=["flex", "ssv"],
    public=True,
    permission_classes=[permissions.AllowAny],
)

schema_cache_timeout = 60 * 5  # 5 minutes

swagger_urlpatterns = [
    path(
        "",
        schema_view.with_ui("swagger", cache_timeout=schema_cache_timeout),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=schema_cache_timeout),
        name="schema-json",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=schema_cache_timeout),
        name="schema-redoc",
    ),
]

urlpatterns_v1 = [
    path(
        "",
        include("safe_locking_service.locking_events.urls", namespace="locking_events"),
    ),
    path(
        "campaigns/",
        include("safe_locking_service.campaigns.urls", namespace="locking_campaigns"),
    ),
]

urlpatterns = swagger_urlpatterns + [
    path(settings.ADMIN_URL, admin.site.urls),
    path("api/v1/", include((urlpatterns_v1, "v1"))),
    path("check/", lambda request: HttpResponse("Ok"), name="check"),
]


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns

    if not settings.AWS_S3_STORAGE_BACKEND_CONFIGURED:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
admin.autodiscover()
