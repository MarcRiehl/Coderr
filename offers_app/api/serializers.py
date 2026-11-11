from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import transaction

from rest_framework import serializers
from offers_app.models import Offer, OfferDetail

User = get_user_model()


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        return f"/offerdetails/{obj.pk}/"


class OfferUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username"
        ]


class OfferListSerializer(serializers.ModelSerializer):
    details = OfferDetailLinkSerializer(many=True, read_only=True)

    user_details = OfferUserSerializer(source="user", read_only=True)

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

    def get_attribute(self, instance):
        value = super().get_attribute(instance)

        return -1 if value is None else value

    def to_internal_value(self, data):
        if data == -1 or data == "-1":
            return None

        value = super().to_internal_value(data)

        if value < 0:
            raise serializers.ValidationError(
                "Ensure this value is greater than or equal to 0."
            )

        return value

    def to_representation(self, value):
        return int(value)


class OfferDetailSerializer(serializers.ModelSerializer):

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
        if value not in OfferDetail.OfferType.values:
            raise serializers.ValidationError(
                "Invalid offer type."
            )

        return value

class OfferSerializer(serializers.ModelSerializer):

    details = OfferDetailSerializer(many=True)

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

    @transaction.atomic #@transaction.atomic mehrere Datenbankoperationen als eine gemeinsame Transaktion, bei Fehler Rollback
    def create(self, validated_data):
        details_data = validated_data.pop("details")

        offer = Offer.objects.create(**validated_data)

        for detail_data in details_data:
            OfferDetail.objects.create(
                offer=offer,
                **detail_data
            )

        return offer

    @transaction.atomic #s.o.
    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)

        
        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()# Aktualisiert nur submitted Angebotfelder

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

                detail.save() # Aktualisiert nur submitted details

        return instance

class OfferDetailAbsoluteLinkSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="offer-detail-detail") #erzeugt es automatisch eine absolute URL

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]


class OfferRetrieveSerializer(serializers.ModelSerializer):
    details = OfferDetailAbsoluteLinkSerializer(many=True, read_only=True)

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