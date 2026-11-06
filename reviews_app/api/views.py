from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter

from ..models import Review
from .serializers import ReviewSerializer
from .permissions import IsCustomer, IsReviewOwner


class ReviewViewSet(viewsets.ModelViewSet):

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
        queryset = super().get_queryset()

        business_user_id = self.request.query_params.get('business_user_id')
        reviewer_id = self.request.query_params.get('reviewer_id')

        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)

        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)

        return queryset

    def get_permissions(self):

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
        serializer.save(reviewer=self.request.user)