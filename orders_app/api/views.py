from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders_app.models import Order

from .permissions import IsBusinessOrderOwner, IsCustomer
from .serializers import (OrderCountSerializer, OrderCreateSerializer,
                          OrderSerializer, OrderStatusUpdateSerializer)

User = get_user_model()


class OrderViewSet(viewsets.ModelViewSet):
    """API viewset for listing, creating and updating orders."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch']

    def get_permissions(self):
        """Return the permissions for the current action.

        Customers can create orders, only the business user of an order can
        update it, and any logged-in user can view their own orders.

        Returns:
            list[BasePermission]: The permission instances for the action.
        """
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsCustomer]

        elif self.action == 'partial_update':
            permission_classes = [IsAuthenticated, IsBusinessOrderOwner]

        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsAdminUser]

        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return the serializer class for the current action.

        Returns:
            type[Serializer]: OrderCreateSerializer for create,
                OrderStatusUpdateSerializer for partial_update, otherwise
                OrderSerializer.
        """
        if self.action == 'create':
            return OrderCreateSerializer

        if self.action == 'partial_update':
            return OrderStatusUpdateSerializer

        return OrderSerializer

    def get_queryset(self):
        """Return the orders for the current action.

        For updates, all orders are returned so that permissions decide on
        access. Otherwise, only orders where the user is the customer or the
        business user are returned, newest first.

        Returns:
            QuerySet: The orders for the current action.
        """
        user = self.request.user

        if self.action == 'partial_update':
            return Order.objects.select_related(
                'customer_user',
                'business_user',
                'offer_detail',
                'offer_detail__offer'
            )

        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user)
        ).select_related(
            'customer_user',
            'business_user',
            'offer_detail',
            'offer_detail__offer'
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """Create an order from an offer detail.

        Args:
            request (Request): The HTTP request with ``offer_detail_id``.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: The created order with status 201.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = serializer.save()

        response_serializer = OrderSerializer(
            order, context=self.get_serializer_context())

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        """Update the status of an order.

        Args:
            request (Request): The HTTP request with the new ``status``.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: The updated order with status 200.
        """
        order = self.get_object()

        serializer = self.get_serializer(
            order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_serializer = OrderSerializer(
            order, context=self.get_serializer_context())

        return Response(response_serializer.data)


class OrderCountView(APIView):
    """API view for the number of a business user's orders in progress."""
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Return the number of orders in progress for a business user.

        Args:
            request (Request): The HTTP request.
            business_user_id (int): The ID of the business user.

        Returns:
            Response: The ``order_count`` with status 200.

        Raises:
            Http404: If no business user with this ID exists.
        """
        business_user = get_object_or_404(
            User, id=business_user_id, type='business')

        order_count = Order.objects.filter(
            business_user=business_user, status=Order.OrderStatus.IN_PROGRESS).count()

        serializer = OrderCountSerializer({'order_count': order_count})

        return Response(serializer.data, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    """API view for the number of a business user's completed orders."""
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Return the number of completed orders for a business user.

        Args:
            request (Request): The HTTP request.
            business_user_id (int): The ID of the business user.

        Returns:
            Response: The ``completed_order_count`` with status 200.

        Raises:
            Http404: If no business user with this ID exists.
        """
        business_user = get_object_or_404(
            User, id=business_user_id, type='business')

        completed_order_count = Order.objects.filter(
            business_user=business_user, status=Order.OrderStatus.COMPLETED).count()

        serializer = OrderCountSerializer(
            {'completed_order_count': completed_order_count})

        return Response(serializer.data, status=status.HTTP_200_OK)
