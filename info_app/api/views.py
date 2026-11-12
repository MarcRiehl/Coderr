from django.db.models import Avg, Count
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import Offer
from profiles_app.models import Profile
from reviews_app.models import Review


class BaseInfoView(APIView):
    """API view for general platform statistics."""
    permission_classes = [AllowAny]

    def get(self, request):
        """Return general statistics about the platform.

        Args:
            request (Request): The HTTP request.

        Returns:
            Response: The number of reviews, the average rating rounded
                to one decimal (0.0 if there are no reviews), the number
                of business profiles and the number of offers.
        """

        review_count = Review.objects.count()

        average_rating = Review.objects.aggregate(
            average=Avg('rating'))['average']

        business_profile_count = Profile.objects.filter(
            user__type='business').count()

        offer_count = Offer.objects.count()

        return Response({
            'review_count': review_count,
            'average_rating': round(average_rating, 1) if average_rating is not None else 0.0,
            'business_profile_count': business_profile_count,
            'offer_count': offer_count
        })
