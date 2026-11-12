from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from offers_app.models import OfferDetail
from orders_app.models import Order


class RevisionsField(serializers.IntegerField):
    """Integer field for revisions where -1 means unlimited."""

    def get_attribute(self, instance):
        """Read the revisions value from the instance.

        Args:
            instance (Order): The order.

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
                "Der Wert muss größer oder gleich 0 sein."
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


class OrderSerializer(serializers.ModelSerializer):
    """Read-only serializer for showing orders."""
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False
    )

    revisions = RevisionsField(
        required=False,
        allow_null=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at'
        ]

        read_only_fields = fields


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an order from an offer detail."""
    offer_detail_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ['offer_detail_id']

    def validate_offer_detail_id(self, value):
        """Look up the offer detail with the given ID.

        Args:
            value (int): The ID of the offer detail.

        Returns:
            OfferDetail: The offer detail with its offer and creator.

        Raises:
            NotFound: If no offer detail with this ID exists.
        """
        try:
            return OfferDetail.objects.select_related(
                'offer',
                'offer__user'
            ).get(id=value)

        except OfferDetail.DoesNotExist:
            raise NotFound(
                "Das angegebene Angebotsdetail wurde nicht gefunden."
            )

    @transaction.atomic
    def create(self, validated_data):
        """Create an order with a copy of the offer detail's data.

        The current user becomes the customer and the offer's creator
        becomes the business user.

        Args:
            validated_data (dict): The validated data with the offer detail
                under ``offer_detail_id``.

        Returns:
            Order: The newly created order.
        """
        offer_detail = validated_data['offer_detail_id']
        customer = self.context['request'].user
        business = offer_detail.offer.user

        return Order.objects.create(
            offer_detail=offer_detail,
            customer_user=customer,
            business_user=business,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type
        )


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating only the status of an order."""
    class Meta:
        model = Order
        fields = ['status']

    def to_internal_value(self, data):
        """Reject any field other than ``status`` and validate the input.

        Args:
            data (dict): The request data.

        Returns:
            dict: The validated data.

        Raises:
            ValidationError: If the data contains fields other than
                ``status`` or the status is invalid.
        """
        allowed_fields = set(self.fields.keys())
        received_fields = set(data.keys())

        forbidden_fields = received_fields - allowed_fields

        if forbidden_fields:
            raise serializers.ValidationError({
                field: "Dieses Feld darf nicht geändert werden."
                for field in forbidden_fields
            })

        return super().to_internal_value(data)


class OrderCountSerializer(serializers.Serializer):
    """Serializer for the number of open or completed orders."""
    order_count = serializers.IntegerField(required=False)
    completed_order_count = serializers.IntegerField(required=False)
