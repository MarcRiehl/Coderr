from rest_framework import serializers
from ..models import Order
from offers_app.models import OfferDetail
from django.db import transaction


class OrderSerializer(serializers.ModelSerializer):

    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False
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

    offer_detail_id = serializers.PrimaryKeyRelatedField(
        source='offer_detail',
        queryset=OfferDetail.objects.select_related(
            'offer',
            'offer__user'
        ),
        write_only=True
    )

    class Meta:
        model = Order
        fields = ['offer_detail_id']

    @transaction.atomic
    def create(self, validated_data):
        offer_detail = validated_data['offer_detail']
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

class OrderCountSerializer(serializers.Serializer):
    order_count = serializers.IntegerField(required=False)
    completed_order_count = serializers.IntegerField(required=False)