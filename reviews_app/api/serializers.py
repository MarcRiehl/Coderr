from rest_framework import serializers
from ..models import Review


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'reviewer',
            'created_at',
            'updated_at'
        ]

    def validate_business_user(self, value):
        if value.type != 'business':
            raise serializers.ValidationError(
                "Bewertungen können nur für Business User erstellt werden."
            )
        return value

    def validate(self, attrs):
        business_user = attrs.get(
            'business_user',
            getattr(self.instance, 'business_user', None)
        )

        if self.instance and 'business_user' in attrs:
            raise serializers.ValidationError({
                'business_user': 'Der Business User kann nicht geändert werden.'
            })

        if not self.instance and business_user:
            reviewer = self.context['request'].user

            if Review.objects.filter(
                business_user=business_user,
                reviewer=reviewer
            ).exists():
                raise serializers.ValidationError({
                    'business_user': 'Du hast diesen Business User bereits bewertet.'
                })

        return attrs