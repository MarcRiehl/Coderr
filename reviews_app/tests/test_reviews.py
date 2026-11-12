from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
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

    def test_get_reviews_authenticated(self):
        """A logged-in user gets all reviews with status 200."""
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)

        self.assertEqual(len(results), 2)

    def test_get_reviews_unauthenticated(self):
        """Listing reviews without authentication is rejected."""
        response = self.client.get(self.list_url)

        self.assertIn(response.status_code, [
                      status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_get_reviews_filter_business_user_id(self):
        """Filtering by business_user_id returns only that user's reviews."""
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            self.list_url, {'business_user_id': self.business.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['business_user'], self.business.id)

    def test_get_reviews_filter_reviewer_id(self):
        """Filtering by reviewer_id returns only reviews by that reviewer."""
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            self.list_url, {'reviewer_id': self.customer.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)
        self.assertEqual(len(results), 2)

        for review in results:
            self.assertEqual(review['reviewer'], self.customer.id)

    def test_get_reviews_filter_combined(self):
        """Both filters can be combined."""
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

    def test_get_reviews_filter_invalid_ids_return_400(self):
        """Non-numeric business_user_id or reviewer_id returns 400."""
        self.client.force_authenticate(user=self.customer)

        for param in ('business_user_id', 'reviewer_id'):
            with self.subTest(param=param):
                response = self.client.get(self.list_url, {param: 'abc'})

                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(param, response.data)

    def test_get_reviews_ordering_rating_ascending(self):
        """Ordering by rating sorts the reviews from lowest to highest."""
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.list_url, {'ordering': 'rating'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)

        ratings = [review['rating'] for review in results]

        self.assertEqual(ratings, sorted(ratings))

    def test_get_reviews_ordering_rating_descending(self):
        """Ordering by -rating sorts the reviews from highest to lowest."""
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.list_url, {'ordering': '-rating'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)

        ratings = [review['rating'] for review in results]

        self.assertEqual(ratings, sorted(ratings, reverse=True))

    def test_get_reviews_ordering_updated_at(self):
        """Ordering by -updated_at puts the most recently updated review first."""
        self.client.force_authenticate(user=self.customer)

        now = timezone.now()

        Review.objects.filter(pk=self.review.id).update(
            updated_at=now - timedelta(days=2))

        Review.objects.filter(pk=self.review2.id).update(
            updated_at=now - timedelta(days=1))

        response = self.client.get(self.list_url, {'ordering': '-updated_at'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = self.get_results(response)

        self.assertEqual(results[0]['id'], self.review2.id)

    def test_get_single_review_authenticated(self):
        """Any logged-in user can retrieve a single review."""
        self.client.force_authenticate(user=self.customer2)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.review.id)

    def test_create_review_success(self):
        """A customer can create a review and becomes its reviewer."""
        self.client.force_authenticate(user=self.customer2)

        data = {
            'business_user': self.business.id,
            'rating': 5,
            'description': 'Alles war toll!'
        }

        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['business_user'], self.business.id)

        self.assertEqual(response.data['reviewer'], self.customer2.id)

        self.assertEqual(response.data['rating'], 5)

        self.assertTrue(
            Review.objects.filter(
                business_user=self.business, reviewer=self.customer2).exists()
        )

    def test_create_review_unauthenticated(self):
        """Creating a review without authentication is rejected."""
        data = {
            'business_user': self.business.id,
            'rating': 4,
            'description': 'Sehr gut!'
        }

        response = self.client.post(self.list_url, data, format='json')

        self.assertIn(response.status_code, [
                      status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_create_review_only_customer_allowed(self):
        """A business user cannot create a review and gets 403."""
        self.client.force_authenticate(user=self.business2)

        data = {
            'business_user': self.business.id,
            'rating': 4,
            'description': 'Sehr gut!'
        }

        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_review_duplicate_not_allowed(self):
        """Reviewing the same business user twice returns 400."""
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
        """Reviewing a customer instead of a business user returns 400."""
        self.client.force_authenticate(user=self.customer2)

        data = {
            'business_user': self.customer.id,
            'rating': 4,
            'description': 'Testbewertung'
        }

        response = self.client.post(self.list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_invalid_rating(self):
        """A rating above the allowed range returns 400."""
        self.client.force_authenticate(user=self.customer2)

        data = {
            'business_user': self.business.id,
            'rating': 6,
            'description': 'Ungültige Bewertung'
        }

        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_review_success(self):
        """The author can update the rating and description."""
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
        """Another user cannot update the review and gets 403."""
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
        """Updating a review without authentication is rejected."""
        data = {
            'rating': 5,
            'description': 'Test'
        }

        response = self.client.patch(self.detail_url, data, format='json')

        self.assertIn(response.status_code, [
                      status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_update_review_business_user_not_allowed(self):
        """Changing the business user of a review returns 400."""
        self.client.force_authenticate(user=self.customer)

        data = {
            'business_user': self.business2.id
        }

        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_review_reviewer_not_allowed(self):
        """The reviewer field is ignored on update."""
        self.client.force_authenticate(user=self.customer)

        original_reviewer = self.review.reviewer_id

        data = {
            'reviewer': self.customer2.id,
            'rating': 5
        }

        response = self.client.patch(self.detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.review.refresh_from_db()

        self.assertEqual(self.review.reviewer_id, original_reviewer)
        self.assertEqual(self.review.rating, 5)

    def test_update_review_readonly_fields_not_allowed(self):
        """created_at and updated_at cannot be set by the client."""
        self.client.force_authenticate(user=self.customer)

        original_created_at = self.review.created_at
        original_updated_at = self.review.updated_at

        data = {
            'created_at': '2020-01-01T10:00:00Z',
            'updated_at': '2020-01-01T10:00:00Z',
            'rating': 5
        }

        response = self.client.patch(self.detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.review.refresh_from_db()

        self.assertEqual(self.review.created_at, original_created_at)

        self.assertGreater(self.review.updated_at, original_updated_at)

        self.assertEqual(self.review.rating, 5)

    def test_delete_review_success(self):
        """The author can delete the review."""
        self.client.force_authenticate(user=self.customer)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Review.objects.filter(id=self.review.id).exists())

    def test_delete_review_only_owner_allowed(self):
        """Another user cannot delete the review and gets 403."""
        self.client.force_authenticate(user=self.customer2)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertTrue(Review.objects.filter(id=self.review.id).exists())

    def test_delete_review_unauthenticated(self):
        """Deleting a review without authentication is rejected."""
        response = self.client.delete(self.detail_url)

        self.assertIn(response.status_code, [
                      status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_put_method_not_allowed(self):
        """PUT is not allowed and returns 405."""
        self.client.force_authenticate(user=self.customer)

        response = self.client.put(self.detail_url, {}, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_results(self, response):
        if isinstance(response.data, dict) and 'results' in response.data:
            return response.data['results']

        return response.data
