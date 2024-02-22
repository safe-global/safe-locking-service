from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from safe_locking_service import __version__


class AboutView(GenericAPIView):
    """
    Returns information and configuration of the service
    """

    @method_decorator(cache_page(5 * 60))  # 5 minutes
    def get(self, request, format=None):
        content = {
            "name": "Safe Locking Service",
            "version": __version__,
            "api_version": request.version,
            "secure": request.is_secure(),
            "host": request.get_host(),
            "headers": [x for x in request.META.keys() if "FORWARD" in x],
        }
        return Response(content)
