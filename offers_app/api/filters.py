from django.db.models import Q, Min
from rest_framework.exceptions import ValidationError
from decimal import Decimal, InvalidOperation


class OfferFilter:

    ALLOWED_ORDERING = [
        "updated_at",
        "-updated_at",
        "min_price",
        "-min_price"
    ]
        

    def __init__(self, queryset, params):
        self.queryset = queryset
        self.params = params

    def validate_params(self):
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

        creator_id = self.params.get("creator_id")#Filter nach ID
        if creator_id not in (None, ""):
            try:
                if int(creator_id) <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                errors["creator_id"] = "Muss eine positive Ganzzahl sein."
                

        min_price = self.params.get("min_price") #Filter min Preis
        if min_price not in (None, ""):
            try:
                price = Decimal(min_price)
                if not price.is_finite() or price < 0:
                    raise ValueError
            except (InvalidOperation, ValueError, TypeError):
                errors["min_price"] = "Muss eine gültige Zahl größer oder gleich 0 sein."

        max_delivery_time = self.params.get("max_delivery_time")# Filter Lieferzeit
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

    def filter_by_creator(self): #Filter nach ID
        creator_id = self.params.get("creator_id")

        if creator_id not in (None, ""):
            self.queryset = self.queryset.filter(user_id=creator_id)

        return self
    
    def filter_by_min_price(self): #Filter min Preis
        min_price = self.params.get("min_price")

        if min_price not in (None, ""):
            self.queryset = self.queryset.filter(min_price__gte=min_price)

        return self

    def filter_by_max_delivery_time(self): #Filter Lieferzeit
        max_delivery_time = self.params.get("max_delivery_time")

        if max_delivery_time not in (None, ""):
            self.queryset = self.queryset.filter(min_delivery_time__lte=max_delivery_time)

        return self

    def search(self): #Suche im Titel und in der Beschreibung
        search = self.params.get("search")

        if search:
            self.queryset = self.queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))

        return self

    def order(self): #Sortiert die Angebote nach den Feldern 'updated_at' oder 'min_price'.
        ordering = self.params.get("ordering")

        if ordering:
            self.queryset = self.queryset.order_by(ordering)
        else:
            self.queryset = self.queryset.order_by("-updated_at")

        return self

    def apply(self):
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