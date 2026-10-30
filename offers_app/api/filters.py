from django.db.models import Q, Min


class OfferFilter:

    def __init__(self, queryset, params):
        self.queryset = queryset
        self.params = params

    def filter_by_creator(self): #Filter nach ID
        creator_id = self.params.get("creator_id")

        if creator_id:
            self.queryset = self.queryset.filter(user_id=creator_id)

        return self

    def filter_by_min_price(self): #Filter min Preis
        min_price = self.params.get("min_price")

        if min_price:
            self.queryset = self.queryset.filter(min_price__gte=min_price)

        return self

    def filter_by_max_delivery_time(self): #Filter Lieferzeit
        max_delivery_time = self.params.get("max_delivery_time")

        if max_delivery_time:
            self.queryset = self.queryset.filter(min_delivery_time__lte=max_delivery_time)

        return self

    def search(self): #Suche im Titel und in der Beschreibung
        search = self.params.get("search")

        if search:
            self.queryset = self.queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))

        return self

    def order(self): #Sortiert die Angebote nach den Feldern 'updated_at' oder 'min_price'.
        ordering = self.params.get("ordering")

        allowed_ordering = [
            "updated_at",
            "-updated_at",
            "min_price",
            "-min_price"
        ]

        if ordering in allowed_ordering:
            self.queryset = self.queryset.order_by(ordering)
        else:
            self.queryset = self.queryset.order_by("-updated_at")

        return self

    def apply(self):
        return (
            self
            .filter_by_creator()
            .filter_by_min_price()
            .filter_by_max_delivery_time()
            .search()
            .order()
            .queryset
        )