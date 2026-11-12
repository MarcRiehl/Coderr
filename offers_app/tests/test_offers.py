import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from offers_app.models import Offer, OfferDetail

User = get_user_model()


@override_settings(
    MEDIA_ROOT=tempfile.mkdtemp()
)
class OfferTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.business_user = User.objects.create_user(
            username="business1",
            password="testpassword123",
            type="business"
        )

        self.other_business_user = User.objects.create_user(
            username="business2",
            password="testpassword123",
            type="business"
        )

        self.customer_user = User.objects.create_user(
            username="customer1",
            password="testpassword123",
            type="customer"
        )

        self.business_token = Token.objects.create(
            user=self.business_user
        )

        self.other_business_token = Token.objects.create(
            user=self.other_business_user
        )

        self.customer_token = Token.objects.create(
            user=self.customer_user
        )

        self.offer = self.create_offer(self.business_user)

        self.offer_url = reverse("offers-detail", kwargs={"pk": self.offer.pk})

        self.offers_url = reverse("offers-list")

    def authenticate(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def create_offer(self, user, title="Grafikdesign-Paket", basic_price=100, standard_price=200,  premium_price=500):

        offer = Offer.objects.create(
            user=user,
            title=title,
            description="Ein umfassendes Grafikdesign-Paket.",
            image=None
        )

        OfferDetail.objects.create(
            offer=offer,
            title="Basic Design",
            revisions=2,
            delivery_time_in_days=5,
            price=basic_price,
            features=["Logo Design", "Visitenkarte"],
            offer_type="basic"
        )

        OfferDetail.objects.create(
            offer=offer,
            title="Standard Design",
            revisions=5,
            delivery_time_in_days=7,
            price=standard_price,
            features=["Logo Design", "Visitenkarte", "Briefpapier"],
            offer_type="standard"
        )

        OfferDetail.objects.create(
            offer=offer,
            title="Premium Design",
            revisions=10,
            delivery_time_in_days=10,
            price=premium_price,
            features=["Logo Design", "Visitenkarte", "Briefpapier", "Flyer"],
            offer_type="premium"
        )

        return offer

    def valid_offer_data(self):
        return {
            "title": "Neues Grafikdesign-Paket",
            "image": None,
            "description": "Ein neues Grafikdesign-Angebot.",
            "details": [
                {
                    "title": "Basic Design",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Logo Design"],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard Design",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": ["Logo Design", "Flyer"],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium Design",
                    "revisions": 10,
                    "delivery_time_in_days": 10,
                    "price": 500,
                    "features": ["Logo Design", "Flyer", "Briefpapier"],
                    "offer_type": "premium"
                }
            ]
        }

    def test_get_offers_success(self):
        """The offer list returns 200 with min price, min delivery time and user details."""
        response = self.client.get(self.offers_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        offer_data = response.data["results"][0]

        self.assertEqual(offer_data["title"], "Grafikdesign-Paket")
        self.assertEqual(len(offer_data["details"]), 3)

        self.assertEqual(offer_data["min_price"], 100)
        self.assertEqual(offer_data["min_delivery_time"], 5)

        self.assertIn("user_details", offer_data)

    def test_get_offers_unauthenticated(self):
        """The offer list can be accessed without authentication."""
        response = self.client.get(self.offers_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_offers_by_creator(self):
        """Filtering by creator_id returns only that user's offers."""
        response = self.client.get(
            self.offers_url, {"creator_id": self.business_user.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_filter_offers_by_min_price(self):
        """Filtering by min_price excludes cheaper offers."""
        response = self.client.get(self.offers_url, {"min_price": 150})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_filter_offers_by_max_delivery_time(self):
        """Filtering by max_delivery_time returns offers delivered in time."""
        response = self.client.get(self.offers_url, {"max_delivery_time": 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_search_offers(self):
        """Searching returns offers whose title or description matches."""
        response = self.client.get(self.offers_url, {"search": "Grafikdesign"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_filter_and_search_combined(self):
        """Filters and search can be combined."""
        response = self.client.get(
            self.offers_url,
            {
                "creator_id": self.business_user.id,
                "search": "Design",
                "min_price": "50"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_invalid_creator_id_returns_400(self):
        """A non-numeric creator_id returns 400."""
        response = self.client.get(self.offers_url, {"creator_id": "invalid"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_min_price_returns_400(self):
        """A non-numeric min_price returns 400."""
        response = self.client.get(self.offers_url, {"min_price": "invalid"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_max_delivery_time_returns_400(self):
        """A non-numeric max_delivery_time returns 400."""
        response = self.client.get(
            self.offers_url,
            {"max_delivery_time": "invalid"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_ordering_returns_400(self):
        """An unknown ordering field returns 400."""
        response = self.client.get(
            self.offers_url, {"ordering": "invalid_field"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_page_size_returns_400(self):
        """A non-numeric page_size returns 400."""
        response = self.client.get(self.offers_url, {"page_size": "invalid"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_offers_by_min_price(self):
        """Ordering by min_price puts the cheapest offer first."""
        self.create_offer(
            self.business_user,
            title="Website Design",
            basic_price=50,
            standard_price=100,
            premium_price=150
        )

        response = self.client.get(self.offers_url, {"ordering": "min_price"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]

        self.assertEqual(results[0]["title"], "Website Design")
        self.assertEqual(results[0]["min_price"], 50)

    def test_retrieve_offer_without_image(self):
        """An offer without an image returns null for image."""
        self.authenticate(self.business_token)

        response = self.client.get(self.offer_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIsNone(response.data["image"])

    def test_create_offer_success(self):
        """A business user can create an offer with three details."""
        self.authenticate(self.business_token)

        data = self.valid_offer_data()

        response = self.client.post(
            self.offers_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Offer.objects.filter(
            user=self.business_user).count(), 2)

        created_offer = Offer.objects.get(title="Neues Grafikdesign-Paket")

        self.assertEqual(created_offer.details.count(), 3)

    def test_create_offer_unauthenticated(self):
        """Creating an offer without authentication returns 401."""
        response = self.client.post(
            self.offers_url,
            self.valid_offer_data(),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_offer_customer_forbidden(self):
        """A customer cannot create an offer and gets 403."""
        self.authenticate(self.customer_token)

        response = self.client.post(
            self.offers_url, self.valid_offer_data(), format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_offer_without_three_details(self):
        """Creating an offer with fewer than three details returns 400."""
        self.authenticate(self.business_token)

        data = self.valid_offer_data()
        data["details"].pop()

        response = self.client.post(self.offers_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_offer_success(self):
        """A single offer returns its data and absolute detail URLs."""
        self.authenticate(self.business_token)

        response = self.client.get(self.offer_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["id"], self.offer.id)
        self.assertEqual(response.data["title"], "Grafikdesign-Paket")

        self.assertEqual(response.data["min_price"], 100)
        self.assertEqual(response.data["min_delivery_time"], 5)

        self.assertEqual(len(response.data["details"]), 3)

        self.assertIn("/api/offerdetails/", response.data["details"][0]["url"])

    def test_retrieve_offer_unauthenticated(self):
        """Retrieving an offer without authentication returns 401."""
        response = self.client.get(self.offer_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_offer_not_found(self):
        """Retrieving a non-existent offer returns 404."""
        self.authenticate(self.business_token)

        url = reverse("offers-detail", kwargs={"pk": 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_offer_success(self):
        """The owner can update an offer and only the given detail changes."""
        self.authenticate(self.business_token)

        basic_detail = self.offer.details.get(offer_type="basic")
        original_id = basic_detail.id

        data = {
            "title": "Updated Grafikdesign-Paket",
            "details": [
                {
                    "title": "Basic Design Updated",
                    "revisions": 3,
                    "delivery_time_in_days": 6,
                    "price": 120,
                    "features": ["Logo Design", "Flyer"],
                    "offer_type": "basic"
                }
            ]
        }

        response = self.client.patch(
            self.offer_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.offer.refresh_from_db()
        basic_detail.refresh_from_db()

        self.assertEqual(self.offer.title, "Updated Grafikdesign-Paket")
        self.assertEqual(basic_detail.id, original_id)
        self.assertEqual(basic_detail.price, 120)
        self.assertEqual(basic_detail.revisions, 3)

        standard = self.offer.details.get(offer_type="standard")
        premium = self.offer.details.get(offer_type="premium")

        self.assertEqual(standard.price, 200)
        self.assertEqual(premium.price, 500)

        self.assertEqual(len(response.data["details"]), 3)

    def test_update_offer_without_offer_type(self):
        """Updating a detail without offer_type returns 400."""
        self.authenticate(self.business_token)

        data = {
            "details": [
                {
                    "title": "Basic Design Updated",
                    "price": 120
                }
            ]
        }

        response = self.client.patch(self.offer_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_offer_other_business_forbidden(self):
        """Another business user cannot update the offer and gets 403."""
        self.authenticate(self.other_business_token)

        response = self.client.patch(
            self.offer_url, {"title": "Fremdes Angebot"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_offer_customer_forbidden(self):
        """A customer cannot update an offer and gets 403."""
        self.authenticate(self.customer_token)

        response = self.client.patch(
            self.offer_url, {"title": "Neuer Titel"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_offer_unauthenticated(self):
        """Updating an offer without authentication returns 401."""
        response = self.client.patch(
            self.offer_url, {"title": "Neuer Titel"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_offer_not_found(self):
        """Updating a non-existent offer returns 404."""
        self.authenticate(self.business_token)

        url = reverse("offers-detail", kwargs={"pk": 99999})

        response = self.client.patch(
            url, {"title": "Neuer Titel"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_offer_with_image(self):
        """Uploading an image stores it in the user's image folder."""
        self.authenticate(self.business_token)

        image = SimpleUploadedFile(
            name="test.jpg",
            content=b"fake image content",
            content_type="image/jpeg"
        )

        response = self.client.patch(
            self.offer_url,
            data={"image": image},
            format="multipart"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data
        )

        self.offer.refresh_from_db()

        self.assertTrue(self.offer.image)

        self.assertTrue(
            self.offer.image.name.startswith(
                f"offer_images/{self.business_user.id}/"
            )
        )

        self.assertEqual(
            response.data["image"],
            "test.jpg"
        )

        self.assertTrue(
            self.offer.image.storage.exists(
                self.offer.image.name
            )
        )

    # Tests für Offer DELETE ID
    def test_delete_offer_success(self):
        """The owner can delete an offer together with its details."""
        self.authenticate(self.business_token)

        response = self.client.delete(self.offer_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Offer.objects.filter(pk=self.offer.pk).exists())

        self.assertEqual(OfferDetail.objects.filter(
            offer=self.offer).count(), 0)

    def test_delete_offer_other_business_forbidden(self):
        """Another business user cannot delete the offer and gets 403."""
        self.authenticate(self.other_business_token)

        response = self.client.delete(self.offer_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_offer_customer_forbidden(self):
        """A customer cannot delete an offer and gets 403."""
        self.authenticate(self.customer_token)

        response = self.client.delete(self.offer_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_offer_unauthenticated(self):
        """Deleting an offer without authentication returns 401."""
        response = self.client.delete(self.offer_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_offer_detail_success(self):
        """A single offer detail returns its data."""
        detail = self.offer.details.get(offer_type="basic")

        url = reverse("offer-detail-detail", kwargs={"pk": detail.pk})

        self.authenticate(self.business_token)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["id"], detail.id)
        self.assertEqual(response.data["title"], "Basic Design")
        self.assertEqual(response.data["price"], 100)
        self.assertEqual(response.data["offer_type"], "basic")

    def test_retrieve_offer_detail_unauthenticated(self):
        """Retrieving an offer detail without authentication returns 401."""
        detail = self.offer.details.get(offer_type="basic")

        url = reverse("offer-detail-detail", kwargs={"pk": detail.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_offer_detail_not_found(self):
        """Retrieving a non-existent offer detail returns 404."""
        self.authenticate(self.business_token)

        url = reverse("offer-detail-detail", kwargs={"pk": 99999})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_offers_pagination(self):
        """page_size limits the results and a next link is returned."""
        self.create_offer(self.business_user, title="Website Design")

        response = self.client.get(self.offers_url, {"page_size": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIsNotNone(response.data["next"])

    def test_patch_offer_image(self):
        """An uploaded image keeps its file name and is saved to storage."""
        self.authenticate(self.business_token)

        image = SimpleUploadedFile(
            name="offer-image.jpg",
            content=b"fake image content",
            content_type="image/jpeg"
        )

        response = self.client.patch(
            self.offer_url,
            data={"image": image},
            format="multipart"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data
        )

        self.offer.refresh_from_db()

        self.assertTrue(self.offer.image)

        self.assertTrue(
            self.offer.image.name.startswith(
                f"offer_images/{self.business_user.id}/"
            )
        )

        self.assertTrue(
            self.offer.image.name.endswith("offer-image.jpg")
        )

        self.assertEqual(
            response.data["image"],
            "offer-image.jpg"
        )

        self.assertTrue(
            self.offer.image.storage.exists(
                self.offer.image.name
            )
        )
