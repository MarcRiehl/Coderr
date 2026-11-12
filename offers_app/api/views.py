from django.db.models import Min
from rest_framework.generics import RetrieveAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from ..models import Offer, OfferDetail
from .filters import OfferFilter
from .pagination import OfferPagination
from .permissions import IsBusinessUser, IsOfferOwner
from .serializers import (OfferDetailSerializer, OfferListSerializer,
                          OfferRetrieveSerializer, OfferSerializer)


class OfferViewSet(ModelViewSet):
    """API viewset for listing, creating, showing, updating and deleting offers."""
    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Offer.objects.all()
    pagination_class = OfferPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        """Return the permissions for the current action.

        Anyone can list offers, logged-in users can view a single offer,
        business users can create offers, and only the owner can update or
        delete an offer.

        Returns:
            list[BasePermission]: The permission instances for the action.
        """
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
        """Return the serializer class for the current action.

        Returns:
            type[Serializer]: OfferListSerializer for list,
                OfferRetrieveSerializer for retrieve, otherwise OfferSerializer.
        """
        if self.action == "list":
            return OfferListSerializer

        if self.action == "retrieve":
            return OfferRetrieveSerializer

        return OfferSerializer

    def get_queryset(self):
        """Return the offers with their minimum price and delivery time.

        For the list action, the query parameters are used to filter, search
        and sort the offers.

        Returns:
            QuerySet: The offers for the current action.

        Raises:
            ValidationError: If the query parameters of the list are invalid.
        """
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
        """Save a new offer with the current user as its creator.

        Args:
            serializer (OfferSerializer): The validated serializer.

        Returns:
            None
        """
        serializer.save(user=self.request.user)


class OfferDetailsView(RetrieveAPIView):
    """API view for showing a single offer detail to logged-in users."""
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
