from rest_framework.views import APIView
from rest_framework import generics, mixins, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import ProfileSerializer

class ProfileViewSet(ModelViewSet):
    http_method_names = ['get', 'patch']

    serializer_class = ProfileSerializer

    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        pass

    def get_serializer_class(self):
        pass




class ProfileBusinessViewSet(APIView):
    pass

class ProfileCustomerViewSet(APIView):
    pass