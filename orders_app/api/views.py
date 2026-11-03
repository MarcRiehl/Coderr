from rest_framework.views import APIView
from rest_framework import generics, mixins, status
from rest_framework.viewsets import ModelViewSet

from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .permissions import IsCustomer
from .serializers import OrderSerializer
from ..models import Order

class OrderViewSet(viewsets.ModelViewSet):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']


    def get_permissions(self):

        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsCustomer]

        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user

        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user)).order_by('-created_at')
    
class OrderCountView(APIView):
    pass

class CompletedOrderCountView(APIView):
    pass