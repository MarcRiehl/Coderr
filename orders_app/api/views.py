from rest_framework.views import APIView
from rest_framework import generics, mixins, status
from rest_framework.viewsets import ModelViewSet

class OrderViewSet(ModelViewSet):
    pass

class OrderCountView(APIView):
    pass

class CompletedOrderCountView(APIView):
    pass