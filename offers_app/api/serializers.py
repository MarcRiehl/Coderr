import os

from django.contrib.auth import get_user_model
from django.db import transaction
from django.urls import reverse
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail

User = get_user_model()


class OfferImageField(serializers.FileField):
    """File field that returns only the file name of an offer image."""

    def to_representation(self, value):
        """Return the file name of the image.

        Args:
            value (FieldFile): The stored image file.

        Returns:
            str | None: The file name without its path, or None if there is
                no image.
        """
        if not value:
            return None

        return os.path.basename(value.name)


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Serializer for offer details as ID and relative URL."""
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        """Build the relative URL of an offer detail.

        Args:
            obj (OfferDetail): The offer detail.

        Returns:
            str: The relative URL of the offer detail.
        """
        return f"/offerdetails/{obj.pk}/"


class OfferUserSerializer(serializers.ModelSerializer):
    """Serializer for the name and username of an offer's creator."""
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username"
        ]


class OfferListSerializer(serializers.ModelSerializer):
    """Serializer for offers in the offer list."""
    details = OfferDetailLinkSerializer(many=True, read_only=True)

    user_details = OfferUserSerializer(source="user", read_only=True)

    image = OfferImageField(required=False, allow_null=True)

    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        coerce_to_string=False
    )

    min_delivery_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details"
        ]


class RevisionsField(serializers.IntegerField):
    """Integer field for revisions where -1 means unlimited."""

    def get_attribute(self, instance):
        """Read the revisions value from the instance.

        Args:
            instance (OfferDetail): The offer detail.

        Returns:
            int: The number of revisions, or -1 if unlimited.
        """
        value = super().get_attribute(instance)

        return -1 if value is None else value

    def to_internal_value(self, data):
        """Convert the input to the value stored in the database.

        Args:
            data (int | str): The input value. -1 means unlimited.

        Returns:
            int | None: The number of revisions, or None if unlimited.

        Raises:
            ValidationError: If the value is not an integer or is less
                than -1.
        """
        if data == -1 or data == "-1":
            return None

        value = super().to_internal_value(data)

        if value < 0:
            raise serializers.ValidationError(
                "Ensure this value is greater than or equal to 0."
            )

        return value

    def to_representation(self, value):
        """Return the revisions value as an integer.

        Args:
            value (int): The number of revisions.

        Returns:
            int: The number of revisions.
        """
        return int(value)


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serializer for creating, updating and showing offer details."""
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False,
        min_value=0
    )

    revisions = RevisionsField(
        required=False,
        allow_null=True
    )

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]
        read_only_fields = ["id"]

    def validate_offer_type(self, value):
        """Check that the offer type is valid.

        Args:
            value (str): The offer type.

        Returns:
            str: The offer type if it is valid.

        Raises:
            ValidationError: If the offer type is not allowed.
        """
        if value not in OfferDetail.OfferType.values:
            raise serializers.ValidationError(
                "Invalid offer type."
            )

        return value


class OfferSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating offers with their details."""
    details = OfferDetailSerializer(many=True)

    image = OfferImageField(required=False, allow_null=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "title",
            "image",
            "description",
            "details",
        ]
        read_only_fields = ["id"]

    def validate_details(self, details):
        """Check the offer details for creating or updating an offer.

        On create, exactly one basic, one standard and one premium detail
        are required. On update, each detail needs a unique ``offer_type``.

        Args:
            details (list[dict]): The validated offer details.

        Returns:
            list[dict]: The details if they are valid.

        Raises:
            ValidationError: If the details do not meet these rules.
        """
        offer_types = [
            detail.get("offer_type")
            for detail in details
        ]

        if not self.instance:
            expected_types = {"basic", "standard", "premium"}

            if len(details) != 3 or set(offer_types) != expected_types:
                raise serializers.ValidationError(
                    "An offer must contain exactly three details: "
                    "basic, standard and premium."
                )

        else:
            if any(not offer_type for offer_type in offer_types):
                raise serializers.ValidationError(
                    "Each detail must include offer_type."
                )

            if len(offer_types) != len(set(offer_types)):
                raise serializers.ValidationError(
                    "Each offer_type can only be updated once."
                )

        return details

    @transaction.atomic
    def create(self, validated_data):
        """Create an offer together with its details.

        Args:
            validated_data (dict): The validated offer data, including
                ``details``.

        Returns:
            Offer: The newly created offer.
        """
        details_data = validated_data.pop("details")

        offer = Offer.objects.create(**validated_data)

        for detail_data in details_data:
            OfferDetail.objects.create(
                offer=offer,
                **detail_data
            )

        return offer

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update an offer and the details given by ``offer_type``.

        Args:
            instance (Offer): The offer to update.
            validated_data (dict): The validated fields to change, optionally
                including ``details``.

        Returns:
            Offer: The updated offer.

        Raises:
            ValidationError: If the offer has no detail with a given
                ``offer_type``.
        """
        details_data = validated_data.pop("details", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        if details_data is not None:
            for detail_data in details_data:
                offer_type = detail_data.pop("offer_type")

                try:
                    detail = instance.details.get(
                        offer_type=offer_type
                    )
                except OfferDetail.DoesNotExist:
                    raise serializers.ValidationError({
                        "details": (
                            f"No detail with offer_type "
                            f"'{offer_type}' exists for this offer."
                        )
                    })

                for field, value in detail_data.items():
                    setattr(detail, field, value)

                detail.save()

        return instance


class OfferDetailAbsoluteLinkSerializer(serializers.ModelSerializer):
    """Serializer for offer details as ID and absolute URL."""
    url = serializers.HyperlinkedIdentityField(view_name="offer-detail-detail")

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]


class OfferRetrieveSerializer(serializers.ModelSerializer):
    """Serializer for showing a single offer."""
    details = OfferDetailAbsoluteLinkSerializer(many=True, read_only=True)
    image = OfferImageField(required=False, allow_null=True)

    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        coerce_to_string=False
    )

    min_delivery_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time"
        ]
