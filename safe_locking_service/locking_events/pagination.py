from django.http import HttpRequest

from rest_framework.pagination import LimitOffsetPagination


class SmallPagination(LimitOffsetPagination):
    max_limit = 100
    default_limit = 10


class CustomListPagination(LimitOffsetPagination):
    max_limit = 100
    default_limit = 10

    def __init__(self, request: HttpRequest):
        super().__init__()
        self.request = request
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)
        self.count: int = None

    def set_count(self, value):
        self.count = value
