from rest_framework.views import APIView
from rest_framework import generics, mixins, status
from rest_framework.viewsets import ModelViewSet

class ProfileViewSet(ModelViewSet):
    pass

class ProfileBusinessViewSet(APIView):
    pass

class ProfileCustomerViewSet(APIView):
    pass