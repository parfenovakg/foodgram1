from rest_framework.pagination import PageNumberPagination

from foodgram.const import DEFAULT_PAGE_SIZE


class PageNumberPaginationWithLimit(PageNumberPagination):
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'limit'
