from django.db.models import Min
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from .permissions import IsBusinessUser

from ..models import Offer
from .serializers import OfferSerializer, OfferListSerializer
from .filters import OfferFilter
from .pagination import OfferPagination


class OfferViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Offer.objects.all()
    pagination_class = OfferPagination

    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]
    
        if self.action == "retrieve":
            return [IsAuthenticated()]
    
        return [IsAuthenticated(), IsBusinessUser()]

    def get_serializer_class(self):
        if self.action == "list":
            return OfferListSerializer

        return OfferSerializer #noch schreiben validate

    def get_queryset(self):
        queryset = Offer.objects.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days")
        ).prefetch_related("details", "user") #annotate macht die berechnung direkt in der Datenbank

        if self.action == "list":
            return OfferFilter(queryset, self.request.query_params).apply()

        return queryset
    
    def perform_create(self, serializer):
        pass

    def partial_update(self, request, *args, **kwargs):
        pass

    def destroy(self, request, *args, **kwargs):
        pass

class OfferDetailsView(RetrieveAPIView): #einzelnes Objekt abrufen /api/offerdetails/{id}/
    pass
