
# python manage.py test reviews_app.tests.test_reviews --settings=core.test_settings

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from reviews_app.models import Review


User = get_user_model()


class ReviewAPITest(APITestCase):

    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer',
            password='testpassword123',
            type='customer'
        )

        self.customer2 = User.objects.create_user(
            username='customer2',
            password='testpassword123',
            type='customer'
        )

        self.business = User.objects.create_user(
            username='business',
            password='testpassword123',
            type='business'
        )

        self.business2 = User.objects.create_user(
            username='business2',
            password='testpassword123',
            type='business'
        )

        self.review = Review.objects.create(
            business_user=self.business,
            reviewer=self.customer,
            rating=4,
            description='Sehr guter Service.'
        )

        self.review2 = Review.objects.create(
            business_user=self.business2,
            reviewer=self.customer,
            rating=5,
            description='Top Qualität!'
        )

        self.list_url = reverse('reviews-list')
        self.detail_url = reverse(
            'reviews-detail',
            kwargs={'pk': self.review.id}
        )

    #Tests GET
    def test_get_reviews_authenticated(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)

        self.assertEqual(len(results), 2)

    def test_get_reviews_unauthenticated(self):
        response = self.client.get(self.list_url)

        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_get_reviews_filter_business_user_id(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.list_url, {'business_user_id': self.business.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['business_user'],self.business.id)

    def test_get_reviews_filter_reviewer_id(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.list_url,{'reviewer_id': self.customer.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)
        self.assertEqual(len(results), 2)

        for review in results:
            self.assertEqual(review['reviewer'], self.customer.id)

    def test_get_reviews_filter_combined(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            self.list_url,
            {
                'business_user_id': self.business.id,
                'reviewer_id': self.customer.id
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)

        self.assertEqual(len(results), 1)

    def test_get_reviews_ordering_rating_ascending(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.list_url,{'ordering': 'rating'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)

        ratings = [review['rating'] for review in results]

        self.assertEqual(ratings, sorted(ratings))

    def test_get_reviews_ordering_rating_descending(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.list_url,{'ordering': '-rating'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)

        ratings = [review['rating'] for review in results]

        self.assertEqual(ratings, sorted(ratings, reverse=True))

    def test_get_reviews_ordering_updated_at(self):
        self.client.force_authenticate(user=self.customer)

        now = timezone.now()

        Review.objects.filter(pk=self.review.id).update(updated_at=now - timedelta(days=2))

        Review.objects.filter(pk=self.review2.id).update(updated_at=now - timedelta(days=1))

        response = self.client.get(self.list_url,{'ordering': '-updated_at'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)

        self.assertEqual(results[0]['id'], self.review2.id)

    def test_get_single_review_authenticated(self):
        self.client.force_authenticate(user=self.customer2)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.review.id)


    #Tests POST
    def test_create_review_success(self):
        self.client.force_authenticate(user=self.customer2)

        data = {
            'business_user': self.business.id,
            'rating': 5,
            'description': 'Alles war toll!'
        }

        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['business_user'],self.business.id)

        self.assertEqual(response.data['reviewer'], self.customer2.id)

        self.assertEqual(response.data['rating'], 5)

        self.assertTrue(
            Review.objects.filter(business_user=self.business, reviewer=self.customer2).exists()
        )

    def test_create_review_unauthenticated(self):
        data = {
            'business_user': self.business.id,
            'rating': 4,
            'description': 'Sehr gut!'
        }

        response = self.client.post(self.list_url,data, format='json')

        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_create_review_only_customer_allowed(self):
        self.client.force_authenticate(user=self.business2)

        data = {
            'business_user': self.business.id,
            'rating': 4,
            'description': 'Sehr gut!'
        }

        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_review_duplicate_not_allowed(self):
        self.client.force_authenticate(user=self.customer)

        data = {
            'business_user': self.business.id,
            'rating': 5,
            'description': 'Noch eine Bewertung!'
        }

        response = self.client.post(
            self.list_url,
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_only_business_user_can_be_reviewed(self):
        self.client.force_authenticate(user=self.customer2)

        data = {
            'business_user': self.customer.id,
            'rating': 4,
            'description': 'Testbewertung'
        }

        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual( response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_invalid_rating(self):
        self.client.force_authenticate(user=self.customer2)

        data = {
            'business_user': self.business.id,
            'rating': 6,
            'description': 'Ungültige Bewertung'
        }

        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #Test Patch
    def test_update_review_success(self):
        self.client.force_authenticate(user=self.customer)

        data = {
            'rating': 5,
            'description': 'Noch besser als erwartet!'
        }

        response = self.client.patch(self.detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.review.refresh_from_db()

        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.description, 'Noch besser als erwartet!')

    def test_update_review_only_owner_allowed(self):
        self.client.force_authenticate(user=self.customer2)

        data = {
            'rating': 2,
            'description': 'Fremde Bewertung ändern'
        }

        response = self.client.patch(self.detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 4)

    def test_update_review_unauthenticated(self):
        data = {
            'rating': 5,
            'description': 'Test'
        }

        response = self.client.patch(self.detail_url, data, format='json')

        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_update_review_business_user_not_allowed(self):
        self.client.force_authenticate(user=self.customer)

        data = {
            'business_user': self.business2.id
        }

        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #Tests DELETE
    def test_delete_review_success(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Review.objects.filter(id=self.review.id).exists())

    def test_delete_review_only_owner_allowed(self):
        self.client.force_authenticate(user=self.customer2)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertTrue(Review.objects.filter(id=self.review.id).exists())

    def test_delete_review_unauthenticated(self):
        response = self.client.delete(self.detail_url)

        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    #Test HTTP Methods
    def test_put_method_not_allowed(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.put(self.detail_url,{},format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    #Test Helper
    def get_results(self, response):
        if isinstance(response.data, dict) and 'results' in response.data: #paginierte oder nicht paginierte 
            return response.data['results']

        return response.data
