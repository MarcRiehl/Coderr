import os

from django.conf import settings
from django.http import FileResponse, Http404
from django.utils import timezone
from django.views import View
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ..models import Profile
from .serializers import (ProfilesBusinessSerializer,
                          ProfilesCustomerSerializer, ProfileSerializer)


class ProfileViewSet(ModelViewSet):
    """API viewset for showing and updating user profiles."""
    http_method_names = ["get", "patch"]

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        """Return all profiles with their users.

        Returns:
            QuerySet: All profiles.
        """
        return Profile.objects.select_related("user").all()

    def get_object(self):
        """Return the profile of the user given by ``pk`` in the URL.

        Returns:
            Profile: The profile of the user.

        Raises:
            Http404: If the user has no profile.
        """
        profile = Profile.objects.filter(
            user_id=self.kwargs["pk"]
        ).first()

        if profile is None:
            raise Http404

        self.check_object_permissions(self.request, profile)
        return profile

    def partial_update(self, request, *args, **kwargs):
        """Update the profile and user data of the current user.

        Also sets ``uploaded_at`` when a new file is uploaded.

        Args:
            request (Request): The HTTP request with the fields to change.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: The updated profile with status 200.

        Raises:
            PermissionDenied: If the profile belongs to another user.
            Http404: If the user has no profile.
        """
        profile = self.get_object()

        if profile.user_id != request.user.id:
            raise PermissionDenied(
                "You can only update your own profile."
            )

        data = request.data.copy()

        user_fields = ["first_name", "last_name", "email"]

        user_data = {
            field: data.get(field)
            for field in user_fields
            if field in data
        }

        serializer = self.get_serializer(profile, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = profile.user

        for field, value in user_data.items():
            setattr(user, field, value)

        if user_data:
            user.save(update_fields=list(user_data.keys()))

        if "file" in request.FILES:
            profile.uploaded_at = timezone.now()
            profile.save(update_fields=["uploaded_at"])

        return Response(self.get_serializer(profile).data, status=status.HTTP_200_OK)


class ProfilesBusinessView(ListAPIView):
    """API view for listing all business profiles."""
    serializer_class = ProfilesBusinessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return all business profiles with their users.

        Returns:
            QuerySet: The profiles of business users.
        """
        return Profile.objects.filter(user__type="business").select_related("user")


class ProfilesCustomerView(ListAPIView):
    """API view for listing all customer profiles."""
    serializer_class = ProfilesCustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return all customer profiles with their users.

        Returns:
            QuerySet: The profiles of customer users.
        """
        return Profile.objects.filter(user__type="customer").select_related("user")


class ProfileOfferImageView(View):
    """View for serving profile and offer images by file name."""
    def get(self, request, filename):
        """Find an image by file name and return it.

        Searches the profile and offer image folders, including subfolders.

        Args:
            request (HttpRequest): The HTTP request.
            filename (str): The file name of the image.

        Returns:
            FileResponse: The image file.

        Raises:
            Http404: If no image with this file name exists.
        """
        image_directories = [
            settings.MEDIA_ROOT / "profile_images",
            settings.MEDIA_ROOT / "offer_images",
        ]

        for directory in image_directories:
            for root, dirs, files in os.walk(directory):
                if filename in files:
                    file_path = os.path.join(root, filename)

                    return FileResponse(
                        open(file_path, "rb")
                    )

        raise Http404("Image not found")
