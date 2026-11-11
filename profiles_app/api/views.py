from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.conf import settings
from django.http import FileResponse, Http404
from django.views import View
import os

from ..models import Profile
from .serializers import (ProfilesBusinessSerializer, ProfilesCustomerSerializer, ProfileSerializer)


class ProfileViewSet(ModelViewSet):
    http_method_names = ["get", "patch"]

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return Profile.objects.select_related("user").all()

    def get_object(self):
        profile = Profile.objects.filter(
            user_id=self.kwargs["pk"]
        ).first()

        if profile is None:
            from django.http import Http404
            raise Http404

        self.check_object_permissions(self.request, profile)
        return profile

    def partial_update(self, request, *args, **kwargs):
        profile = self.get_object()

       
        if profile.user_id != request.user.id:  # Nur der Eigentümer darf das Profil bearbeiten
            raise PermissionDenied(
                "You can only update your own profile."
            )

        data = request.data.copy()

        
        user_fields = ["first_name", "last_name", "email"] # User-Felder vom Profil trennen, alte Version erzeugte Fehler ['Testbsp'] = QueryDict
        
        user_data = {
            field: data.get(field)
            for field in user_fields
            if field in data
        }

        serializer = self.get_serializer(profile, data=data,partial=True) # Profil validieren und aktualisieren
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = profile.user #  User aktualisieren.

        for field, value in user_data.items():
            setattr(user, field, value)

        if user_data:
            user.save(update_fields=list(user_data.keys()))

        if "file" in request.FILES: # Upload-Zeitpunkt nur bei neuer Datei aktualisieren.
            profile.uploaded_at = timezone.now()
            profile.save(update_fields=["uploaded_at"])

        return Response(self.get_serializer(profile).data,status=status.HTTP_200_OK)

class ProfilesBusinessView(ListAPIView):
    serializer_class = ProfilesBusinessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user__type="business").select_related("user") #.order_by('username')

class ProfilesCustomerView(ListAPIView):
    serializer_class = ProfilesCustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user__type="customer").select_related("user") #.order_by('username')

class ProfileImageView(View):

    def get(self, request, filename):
        for root, dirs, files in os.walk(
            settings.MEDIA_ROOT / "profile_images"
        ):
            if filename in files:
                file_path = os.path.join(root, filename)

                return FileResponse(
                    open(file_path, "rb")
                )

        raise Http404("Profile image not found")