
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """Page number pagination for offers with validated query parameters."""
    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 50

    def get_page_number(self, request, paginator):
        """Validate the ``page`` query parameter and return the page number.

        Args:
            request (Request): The HTTP request with the query parameters.
            paginator (Paginator): The Django paginator for the queryset.

        Returns:
            int | str: The requested page number.

        Raises:
            ValidationError: If ``page`` is not a positive integer.
        """
        page_number = request.query_params.get(self.page_query_param, 1)

        if page_number != self.last_page_strings:
            try:
                if int(page_number) <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise ValidationError({
                    "page": "Muss eine positive Ganzzahl sein."
                })

        return super().get_page_number(request, paginator)

    def get_page_size(self, request):
        """Validate the ``page_size`` query parameter and return the page size.

        Args:
            request (Request): The HTTP request with the query parameters.

        Returns:
            int: The requested page size, or the default of 6 if not given.

        Raises:
            ValidationError: If ``page_size`` is not an integer between 1
                and 50.
        """
        page_size = request.query_params.get(self.page_size_query_param)

        if page_size is not None:
            try:
                page_size = int(page_size)

                if page_size <= 0 or page_size > self.max_page_size:
                    raise ValueError

            except (ValueError, TypeError):
                raise ValidationError({
                    "page_size": "Muss eine Ganzzahl zwischen 1 und 50 sein."
                })

            return page_size

        return self.page_size
