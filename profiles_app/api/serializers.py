import os

from django.db import transaction
from rest_framework import serializers

from profiles_app.models import Profile

class ProfileFileField(serializers.FileField):
    def to_representation(self, value):
        if not value:
            return None

        return os.path.basename(value.name)
    
class BaseProfileSerializer(serializers.ModelSerializer): # Gemeinsame Update-Logik für Profile und User.

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        with transaction.atomic(): # User-Daten aktualisieren
            if user_data:
                for attr, value in user_data.items():
                    setattr(instance.user, attr, value)

                instance.user.save()

            instance = super().update(instance, validated_data)  # Profile-Daten inklusive Bild aktualisieren

        return instance   
    
class ProfileSerializer(BaseProfileSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", required=False)
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
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", required=False)
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
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", required=False)
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