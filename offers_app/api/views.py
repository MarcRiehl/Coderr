from django.db.models import Min
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from .permissions import IsBusinessUser, IsOfferOwner

from ..models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferListSerializer, OfferRetrieveSerializer, OfferDetailSerializer
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

        if self.action == "create":
            return [IsAuthenticated(), IsBusinessUser()]

        if self.action in ["partial_update", "destroy"]:
            return [
                IsAuthenticated(),
                IsBusinessUser(),
                IsOfferOwner()
            ]

        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "list":
            return OfferListSerializer
        
        if self.action == "retrieve":
            return OfferRetrieveSerializer

        return OfferSerializer

    def get_queryset(self):
        queryset = Offer.objects.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min(
                "details__delivery_time_in_days"
            )
        ).select_related(
            "user"
        ).prefetch_related(
            "details"
        )

        if self.action == "list":
            return OfferFilter(
                queryset,
                self.request.query_params
            ).apply()

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OfferDetailsView(RetrieveAPIView): #einzelnes Objekt abrufen /api/offerdetails/{id}/
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
