from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math

class PostPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        total_pages = math.ceil(self.page.paginator.count / self.page_size)

        return Response({
            'current_page': self.page.number,
            'total_pages': total_pages,
            'total_count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data

        })