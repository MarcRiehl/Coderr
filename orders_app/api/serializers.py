from rest_framework import serializers
from ..models import Order
from offers_app.models import OfferDetail
from django.db import transaction
from rest_framework.exceptions import NotFound


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
        
class OrderSerializer(serializers.ModelSerializer):

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

    offer_detail_id = serializers.IntegerField(write_only=True) # prüfung gültige Ganzzahl übergeben

    class Meta:
        model = Order
        fields = ['offer_detail_id']

    
    def validate_offer_detail_id(self, value):
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

    class Meta:
        model = Order
        fields = ['status']

    def to_internal_value(self, data):
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
    order_count = serializers.IntegerField(required=False)
    completed_order_count = serializers.IntegerField(required=False)