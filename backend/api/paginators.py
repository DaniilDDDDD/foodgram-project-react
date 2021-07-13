from rest_framework.pagination import PageNumberPagination


class VariablePageSizePaginator(PageNumberPagination):
    page_size_query_param = 'limit'
