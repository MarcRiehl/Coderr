
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError


class OfferPagination(PageNumberPagination): #noch mit dem frontend abstimmen
    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 50

    def get_page_number(self, request, paginator):
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
