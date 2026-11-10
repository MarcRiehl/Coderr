from rest_framework.views import APIView
from rest_framework import generics, mixins, status
from rest_framework import viewsets
from rest_framework.response import Response


from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .permissions import IsCustomer, IsBusinessOrderOwner
from .serializers import OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer, OrderCountSerializer
from ..models import Order

User = get_user_model()

class OrderViewSet(viewsets.ModelViewSet):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch']


    def get_permissions(self):

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

        if self.action == 'create':
            return OrderCreateSerializer

        if self.action == 'partial_update':
            return OrderStatusUpdateSerializer

        return OrderSerializer

    def get_queryset(self):
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
        
        #select_related Angebote effizienter laden

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = serializer.save()

        response_serializer = OrderSerializer(order, context=self.get_serializer_context())

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()

        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_serializer = OrderSerializer(order, context=self.get_serializer_context())

        return Response(response_serializer.data)
    
class OrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):

        business_user = get_object_or_404(User, id=business_user_id, type='business')

        order_count = Order.objects.filter(business_user=business_user, status=Order.OrderStatus.IN_PROGRESS).count()

        serializer = OrderCountSerializer({'order_count': order_count})

        return Response(serializer.data, status=status.HTTP_200_OK)

class CompletedOrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):

        business_user = get_object_or_404(User, id=business_user_id, type='business')

        completed_order_count = Order.objects.filter(business_user=business_user, status=Order.OrderStatus.COMPLETED).count()

        serializer = OrderCountSerializer({'completed_order_count': completed_order_count})

        return Response(serializer.data, status=status.HTTP_200_OK)