# likes/paginations.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math

class LikePagination(PageNumberPagination):
    page_size = 15

    def get_paginated_response(self, data):
        return Response({
            "count": self.page.paginator.count,
            "total_pages": math.ceil(self.page.paginator.count / self.page_size),
            "current_page": self.page.number,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        })
