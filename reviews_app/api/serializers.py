from rest_framework import serializers

from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for creating, updating and showing reviews."""

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
        """Check that the reviewed user is a business user.

        Args:
            value (User): The user being reviewed.

        Returns:
            User: The user if they are a business user.

        Raises:
            ValidationError: If the user is not a business user.
        """
        if value.type != 'business':
            raise serializers.ValidationError(
                "Bewertungen können nur für Business User erstellt werden."
            )
        return value

    def validate(self, attrs):
        """Check the business user rules for creating and updating reviews.

        On update, the business user cannot be changed. On create, a
        customer can review each business user only once.

        Args:
            attrs (dict): The validated review data.

        Returns:
            dict: The review data if it is valid.

        Raises:
            ValidationError: If the business user is changed on update, or
                the reviewer has already reviewed this business user.
        """
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
