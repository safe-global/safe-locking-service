from rest_framework.pagination import LimitOffsetPagination


class SmallPagination(LimitOffsetPagination):
    max_limit = 100
    default_limit = 10
