from decimal import Decimal, InvalidOperation

from django.db.models import Min, Q
from rest_framework.exceptions import ValidationError


class OfferFilter:
    """Filter, search and sort an offer queryset by query parameters."""
    ALLOWED_ORDERING = [
        "updated_at",
        "-updated_at",
        "min_price",
        "-min_price"
    ]

    def __init__(self, queryset, params):
        """Store the queryset and the query parameters.

        Args:
            queryset (QuerySet): The offers to filter.
            params (QueryDict): The query parameters of the request.
        """
        self.queryset = queryset
        self.params = params

    def validate_params(self):
        """Check the query parameters for unknown keys and invalid values.

        Returns:
            OfferFilter: This filter instance, for method chaining.

        Raises:
            ValidationError: If a parameter is unknown or has an invalid value.
        """
        errors = {}

        allowed_params = {
            "creator_id",
            "min_price",
            "max_delivery_time",
            "ordering",
            "search",
            "page_size",
            "page",
        }

        unknown_params = set(self.params.keys()) - allowed_params

        if unknown_params:
            errors["unknown_params"] = (
                f"Unbekannte Query-Parameter: {', '.join(sorted(unknown_params))}"
            )

        creator_id = self.params.get("creator_id")
        if creator_id not in (None, ""):
            try:
                if int(creator_id) <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                errors["creator_id"] = "Muss eine positive Ganzzahl sein."

        min_price = self.params.get("min_price")
        if min_price not in (None, ""):
            try:
                price = Decimal(min_price)
                if not price.is_finite() or price < 0:
                    raise ValueError
            except (InvalidOperation, ValueError, TypeError):
                errors["min_price"] = "Muss eine gültige Zahl größer oder gleich 0 sein."

        max_delivery_time = self.params.get("max_delivery_time")
        if max_delivery_time not in (None, ""):
            try:
                if int(max_delivery_time) < 0:
                    raise ValueError
            except (ValueError, TypeError):
                errors["max_delivery_time"] = "Muss eine Ganzzahl größer oder gleich 0 sein."

        ordering = self.params.get("ordering")
        if ordering and ordering not in self.ALLOWED_ORDERING:
            errors["ordering"] = (
                "Erlaubt sind: updated_at, -updated_at, min_price, -min_price."
            )

        if errors:
            raise ValidationError(errors)

        return self

    def filter_by_creator(self):
        """Keep only offers by the user given in ``creator_id``.

        Returns:
            OfferFilter: This filter instance, for method chaining.
        """
        creator_id = self.params.get("creator_id")

        if creator_id not in (None, ""):
            self.queryset = self.queryset.filter(user_id=creator_id)

        return self

    def filter_by_min_price(self):
        """Keep only offers whose minimum price is at least ``min_price``.

        Returns:
            OfferFilter: This filter instance, for method chaining.
        """
        min_price = self.params.get("min_price")

        if min_price not in (None, ""):
            self.queryset = self.queryset.filter(min_price__gte=min_price)

        return self

    def filter_by_max_delivery_time(self):
        """Keep only offers deliverable within ``max_delivery_time`` days.

        Returns:
            OfferFilter: This filter instance, for method chaining.
        """
        max_delivery_time = self.params.get("max_delivery_time")

        if max_delivery_time not in (None, ""):
            self.queryset = self.queryset.filter(
                min_delivery_time__lte=max_delivery_time)

        return self

    def search(self):
        """Keep only offers whose title or description contains ``search``.

        Returns:
            OfferFilter: This filter instance, for method chaining.
        """
        search = self.params.get("search")

        if search:
            self.queryset = self.queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search))

        return self

    def order(self):
        """Sort offers by ``ordering``, or by newest update if not given.

        Returns:
            OfferFilter: This filter instance, for method chaining.
        """
        ordering = self.params.get("ordering")

        if ordering:
            self.queryset = self.queryset.order_by(ordering)
        else:
            self.queryset = self.queryset.order_by("-updated_at")

        return self

    def apply(self):
        """Validate the parameters and apply all filters, search and sorting.

        Returns:
            QuerySet: The filtered and sorted offers.

        Raises:
            ValidationError: If the query parameters are invalid.
        """
        return (
            self
            .validate_params()
            .filter_by_creator()
            .filter_by_min_price()
            .filter_by_max_delivery_time()
            .search()
            .order()
            .queryset
        )
