from rest_framework.views import APIView
from rest_framework import generics, mixins, status
from rest_framework import viewsets
from rest_framework.response import Response


from django.db.models import Q

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .permissions import IsCustomer, IsBusinessOrderOwner
from .serializers import OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer
from ..models import Order



class OrderViewSet(viewsets.ModelViewSet):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']


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

        if self.action == 'destroy' and user.is_staff:
            return Order.objects.select_related(
            'customer_user',
            'business_user',
            'offer_detail',
            'offer_detail__offer'
        ) #select_related() um zusammengehörige Daten bereits mit einer Datenbankabfrage abzurufen

        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user)).select_related(
            'customer_user',
            'business_user',
            'offer_detail',
            'offer_detail__offer'
        ).order_by('-created_at') #select_related Angebote effizienter laden

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

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        order.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
class OrderCountView(APIView):
    pass

class CompletedOrderCountView(APIView):
    pass