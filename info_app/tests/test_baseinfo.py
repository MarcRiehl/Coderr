
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from auth_app.models import User
from offers_app.models import Offer
from profiles_app.models import Profile
from reviews_app.models import Review

User = get_user_model()


class BaseInfoTests(APITestCase):

    def setUp(self):
        self.url = '/api/base-info/'

        # Business Users
        self.business_user_1 = User.objects.create_user(
            username='business1',
            email='business1@localhost.de',
            password='testpassword123',
            type='business'
        )

        self.business_user_2 = User.objects.create_user(
            username='business2',
            email='business2@localhost.de',
            password='testpassword123',
            type='business'
        )

        self.customer_1 = User.objects.create_user(
            username='customer1',
            email='customer1@localhost.de',
            password='testpassword123',
            type='customer'
        )

        self.customer_2 = User.objects.create_user(
            username='customer2',
            email='customer2@localhost.de',
            password='testpassword123',
            type='customer'
        )

        self.customer_3 = User.objects.create_user(
            username='customer3',
            email='customer3@localhost.de',
            password='testpassword123',
            type='customer'
        )

        Profile.objects.create(user=self.business_user_1)
        Profile.objects.create(user=self.business_user_2)

        Review.objects.create(
            business_user=self.business_user_1,
            reviewer=self.customer_1,
            rating=4,
            description='Guter Service!'
        )

        Review.objects.create(
            business_user=self.business_user_1,
            reviewer=self.customer_2,
            rating=4,
            description='Sehr gut!'
        )

        Review.objects.create(
            business_user=self.business_user_2,
            reviewer=self.customer_3,
            rating=5,
            description='Top gemacht!'
        )

        Offer.objects.create(
            user=self.business_user_1,
            title='Web Design',
            description='Professional Web Design'
        )

        Offer.objects.create(
            user=self.business_user_2,
            title='Logo Design',
            description='Professional Logo Design'
        )

    def test_get_base_info_success(self):
        """The base info endpoint returns 200."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_base_info_contains_required_fields(self):
        """The response contains exactly the four expected fields."""
        response = self.client.get(self.url)

        self.assertEqual(
            set(response.data.keys()),
            {
                'review_count',
                'average_rating',
                'business_profile_count',
                'offer_count'
            }
        )

    def test_review_count_is_correct(self):
        """The review count matches the number of reviews."""
        response = self.client.get(self.url)

        self.assertEqual(response.data['review_count'], 3)

    def test_average_rating_is_correct(self):
        """The average rating is rounded to one decimal."""
        response = self.client.get(self.url)

        self.assertEqual(response.data['average_rating'], 4.3)

    def test_business_profile_count_is_correct(self):
        """The business profile count matches the number of business profiles."""
        response = self.client.get(self.url)

        self.assertEqual(response.data['business_profile_count'], 2)

    def test_offer_count_is_correct(self):
        """The offer count matches the number of offers."""
        response = self.client.get(self.url)

        self.assertEqual(response.data['offer_count'], 2)

    def test_average_rating_is_zero_without_reviews(self):
        """Without reviews, the count is 0 and the average rating is 0.0."""
        Review.objects.all().delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['review_count'], 0)
        self.assertEqual(response.data['average_rating'], 0.0)

    def test_base_info_is_accessible_without_authentication(self):
        """The endpoint can be accessed without authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
