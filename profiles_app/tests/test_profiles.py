#python manage.py test profiles_app.tests.test_profiles

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from profiles_app.models import Profile

User = get_user_model()


class ProfileTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            first_name="Robert",
            last_name="Rankin",
            email="rankin@localhost.de",
            type="business"
        )

        self.profile = Profile.objects.create(
            user=self.user,
            file="profile_picture.jpg",
            location="Berlin",
            tel="123456789",
            description="Business description",
            working_hours="9-17"
        )

        self.token = Token.objects.create(user=self.user)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        self.profile_url = reverse("profile-detail", kwargs={"pk": self.user.pk},)

        self.business_url = reverse("profiles-business")

    def test_get_profile(self):
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.user.pk)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["first_name"], "Robert")
        self.assertEqual(response.data["last_name"], "Rankin")
        self.assertEqual(response.data["email"], "rankin@localhost.de")
        self.assertEqual(response.data["file"], "profile_picture.jpg")
        self.assertEqual(response.data["location"], "Berlin")
        self.assertEqual(response.data["tel"], "123456789")
        self.assertEqual(response.data["description"], "Business description")
        self.assertEqual(response.data["working_hours"], "9-17")
        self.assertEqual(response.data["type"], "business")

    def test_get_profile_unauthenticated(self):
        client = APIClient()

        response = client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,)

    def test_get_profile_not_found(self):
        user_without_profile = User.objects.create_user(
            username="no_profile",
            password="testpassword"
        )

        url = reverse("profile-detail", kwargs={"pk": user_without_profile.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_profile(self):
        payload = {
            "first_name": "Miri",
            "last_name": "Musterfrau",
            "email": "miri@localhost.de",
            "file": "miri-picture.jpg",
            "location": "Hamburg",
            "tel": "987654321",
            "description": "Updated business description",
            "working_hours": "10-18"
        }

        response = self.client.patch(
            self.profile_url,
            data=payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK,)

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(self.user.first_name, "Miri")
        self.assertEqual(self.user.last_name, "Musterfrau")
        self.assertEqual(self.user.email, "miri@localhost.de")

        self.assertEqual(self.profile.file, "miri-picture.jpg")
        self.assertEqual(self.profile.location, "Hamburg")
        self.assertEqual(self.profile.tel, "987654321")
        self.assertEqual(self.profile.description,"Updated business description")
        self.assertEqual(self.profile.working_hours, "10-18")

    def test_patch_foreign_profile_forbidden(self):
        other_user = User.objects.create_user(
            username="otheruser",
            password="testpassword"
        )

        Profile.objects.create(user=other_user)

        url = reverse("profile-detail", kwargs={"pk": other_user.pk})

        response = self.client.patch(url, data={"location": "Koblenz"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_profile_not_found(self):
        user_without_profile = User.objects.create_user(
            username="missingprofile",
            password="testpassword"
        )

        url = reverse("profile-detail", kwargs={"pk": user_without_profile.pk})

        response = self.client.patch(
            url,
            data={"location": "Berlin"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_business_profiles(self):
        customer = User.objects.create_user(
            username="testcustomer",
            password="testpassword",
            type="customer"
        )
        Profile.objects.create(user=customer)

        business_url = reverse("profiles-business")
        response = self.client.get(business_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["user"], self.user.pk)
        self.assertEqual(response.data[0]["username"], "testuser")
        self.assertEqual(response.data[0]["type"], "business")

        returned_user_ids = [
            profile["user"] for profile in response.data
        ]
        self.assertNotIn(customer.pk, returned_user_ids)

    def test_business_profiles_exclude_customers(self):
        customer = User.objects.create_user(
            username="testcustomer",
            password="testpassword",
            type="customer",
        )

        Profile.objects.create(
            user=customer,
            location="Köln"
        )

        response = self.client.get(self.business_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_user_ids = [
            profile["user"] for profile in response.data
        ]

        self.assertIn(self.user.pk, returned_user_ids)
        self.assertNotIn(customer.pk, returned_user_ids)


    def test_get_customer_profiles(self):
        customer = User.objects.create_user(
            username="testcustomer",
            password="testpassword",
            first_name="Johnny",
            last_name="Test",
            type="customer"
        )

        Profile.objects.create(
            user=customer,
            file="profile_picture_customer.jpg",
            uploaded_at="2023-09-15T09:00:00"
        )

        customer_url = reverse("profiles-customer")
        response = self.client.get(customer_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)

        profile_data = response.data[0]

        self.assertEqual(profile_data["user"], customer.pk)
        self.assertEqual(profile_data["username"], "testcustomer")
        self.assertEqual(profile_data["first_name"], "Johnny")
        self.assertEqual(profile_data["last_name"], "Test")
        self.assertEqual(profile_data["file"], "profile_picture_customer.jpg")
        self.assertEqual(profile_data["type"], "customer")
        self.assertEqual(profile_data["uploaded_at"], "2023-09-15T09:00:00+02:00")


    def test_customer_profiles_exclude_business_users(self):
        url = reverse("profiles-customer")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_user_ids = [profile["user"] for profile in response.data]

        self.assertNotIn(self.user.pk, returned_user_ids)


    def test_get_customer_profiles_unauthenticated(self):
        client = APIClient()

        url = reverse("profiles-customer")
        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)