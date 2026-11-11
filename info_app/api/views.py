from rest_framework.views import APIView
from django.db.models import Avg, Count
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from reviews_app.models import Review
from profiles_app.models import Profile
from offers_app.models import Offer


class BaseInfoView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        review_count = Review.objects.count()

        average_rating = Review.objects.aggregate(average=Avg('rating'))['average'] #Durchschnitt direkt in der Datenbank

        business_profile_count = Profile.objects.filter(user__type='business').count() #user__type__ aus dem user model

        offer_count = Offer.objects.count()

        return Response({
            'review_count': review_count,
            'average_rating': round(average_rating, 1) if average_rating is not None else 0.0,
            'business_profile_count': business_profile_count,
            'offer_count': offer_count
        })