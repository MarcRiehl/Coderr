from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from reviews_app.models import Review

from .permissions import IsCustomer, IsReviewOwner
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """API viewset for listing, creating, updating and deleting reviews."""
    serializer_class = ReviewSerializer
    queryset = Review.objects.select_related(
        'business_user',
        'reviewer'
    )

    http_method_names = ['get', 'post', 'patch', 'delete']

    filter_backends = [OrderingFilter]

    ordering_fields = ['updated_at', 'rating']
    ordering = ['-updated_at']

    def get_queryset(self):
        """Return the reviews, filtered by the query parameters.

        Filters by ``business_user_id`` and ``reviewer_id`` if they are given.

        Returns:
            QuerySet: The matching reviews.

        Raises:
            ValidationError: If ``business_user_id`` or ``reviewer_id`` is
                not a positive integer.
        """
        queryset = super().get_queryset()

        for param in ('business_user_id', 'reviewer_id'):
            value = self.request.query_params.get(param)

            if value:
                if not value.isdigit():
                    raise ValidationError(
                        {param: 'Muss eine positive Ganzzahl sein.'}
                    )

                queryset = queryset.filter(**{param: value})

        return queryset

    def get_permissions(self):
        """Return the permissions for the current action.

        Customers can create reviews, only the author can update or delete
        a review, and any logged-in user can view reviews.

        Returns:
            list[BasePermission]: The permission instances for the action.
        """
        if self.action == 'create':
            permission_classes = [
                IsAuthenticated,
                IsCustomer
            ]

        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [
                IsAuthenticated,
                IsReviewOwner
            ]

        else:
            permission_classes = [
                IsAuthenticated
            ]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Save a new review with the current user as its author.

        Args:
            serializer (ReviewSerializer): The validated serializer.

        Returns:
            None
        """
        serializer.save(reviewer=self.request.user)
