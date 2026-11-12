import os

from django.db import transaction
from rest_framework import serializers

from profiles_app.models import Profile


class ProfileFileField(serializers.FileField):
    """File field that returns only the file name of a profile image."""

    def to_representation(self, value):
        """Return the file name of the profile image.

        Args:
            value (FieldFile): The stored image file.

        Returns:
            str | None: The file name without its path, or None if there is
                no image.
        """
        if not value:
            return None

        return os.path.basename(value.name)


class BaseProfileSerializer(serializers.ModelSerializer):
    """Base serializer that updates a profile together with its user."""
    def update(self, instance, validated_data):
        """Update the profile and the related user fields.

        Args:
            instance (Profile): The profile to update.
            validated_data (dict): The validated fields to change. User fields
                are nested under ``user``.

        Returns:
            Profile: The updated profile.
        """
        user_data = validated_data.pop("user", {})

        with transaction.atomic():
            if user_data:
                for attr, value in user_data.items():
                    setattr(instance.user, attr, value)

                instance.user.save()

            instance = super().update(instance, validated_data)

        return instance


class ProfileSerializer(BaseProfileSerializer):
    """Serializer for showing and updating a single profile."""
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    email = serializers.EmailField(source="user.email", required=False)
    type = serializers.CharField(source="user.type", read_only=True)
    file = ProfileFileField(required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]
        read_only_fields = [
            "user",
            "username",
            "type",
            "uploaded_at",
            "created_at",
        ]


class ProfilesBusinessSerializer(BaseProfileSerializer):
    """Serializer for business profiles in the business profile list."""
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    type = serializers.CharField(source="user.type", read_only=True)
    file = ProfileFileField(required=False, allow_null=True)

    class Meta:
        model = Profile

        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        ]
        read_only_fields = [
            "user",
            "username",
            "type"
        ]


class ProfilesCustomerSerializer(BaseProfileSerializer):
    """Serializer for customer profiles in the customer profile list."""
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    type = serializers.CharField(source="user.type", read_only=True)
    file = ProfileFileField(required=False, allow_null=True)

    class Meta:
        model = Profile

        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "uploaded_at",
            "type",
        ]
        read_only_fields = [
            "user",
            "username",
            "uploaded_at",
            "type"
        ]
