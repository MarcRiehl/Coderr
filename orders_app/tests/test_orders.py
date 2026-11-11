
# python manage.py test orders_app.tests.test_orders --settings=core.test_settings

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from orders_app.models import Order


User = get_user_model()


class OrderTests(APITestCase):

    def setUp(self): 
        self.customer = User.objects.create_user(
            username='customer1',
            password='testpassword123',
            type='customer'
        ) # Users erstellen siehe offers

        self.customer2 = User.objects.create_user(
            username='customer2',
            password='testpassword123',
            type='customer'
        )

        self.business = User.objects.create_user(
            username='business1',
            password='testpassword123',
            type='business'
        )

        self.business2 = User.objects.create_user(
            username='business2',
            password='testpassword123',
            type='business'
        )

        self.admin = User.objects.create_user(
            username='admin_test',
            password='testpassword123',
            type='business',
            is_staff=True
        )

        self.offer = Offer.objects.create(
            user=self.business,
            title='Logo Design',
            description='Professionelles Logo Design'
        ) # Offer erstellen

        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic Design',
            revisions=3,
            delivery_time_in_days=5,
            price=150.00,
            features=['Logo Design', 'Visitenkarten'],
            offer_type=OfferDetail.OfferType.BASIC
        ) # OfferDetail erstellen

        self.other_offer = Offer.objects.create(
            user=self.business2,
            title='Web Design',
            description='Professionelles Web Design'
        )# Zweites Angebot für andere Benutzer

        self.other_offer_detail = OfferDetail.objects.create(
            offer=self.other_offer,
            title='Premium Design',
            revisions=5,
            delivery_time_in_days=10,
            price=500.00,
            features=['Web Design', 'Responsive Design'],
            offer_type=OfferDetail.OfferType.PREMIUM
        )

        
        self.order = Order.objects.create(
            offer_detail=self.offer_detail,
            customer_user=self.customer,
            business_user=self.business,
            title=self.offer_detail.title,
            revisions=self.offer_detail.revisions,
            delivery_time_in_days=self.offer_detail.delivery_time_in_days,
            price=self.offer_detail.price,
            features=self.offer_detail.features,
            offer_type=self.offer_detail.offer_type
        ) # Order erstellen

        self.other_order = Order.objects.create(
            offer_detail=self.other_offer_detail,
            customer_user=self.customer2,
            business_user=self.business2,
            title=self.other_offer_detail.title,
            revisions=self.other_offer_detail.revisions,
            delivery_time_in_days=self.other_offer_detail.delivery_time_in_days,
            price=self.other_offer_detail.price,
            features=self.other_offer_detail.features,
            offer_type=self.other_offer_detail.offer_type
        ) # Order für andere Benutzer

        self.order_list_url = reverse('orders-list')
        self.order_detail_url = reverse('orders-detail',kwargs={'pk': self.order.pk})

    #Tests GET orders
    def test_get_orders_success(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.order_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.order.id)

    def test_get_orders_only_related_to_user(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.order_list_url)

        order_ids = [order['id'] for order in response.data]

        self.assertIn(self.order.id, order_ids)
        self.assertNotIn(self.other_order.id, order_ids)

    def test_get_orders_as_business_user(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.get(self.order_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.order.id)

    def test_get_orders_unauthenticated(self):
        response = self.client.get(self.order_list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    #Tests POST orders
    def test_create_order_success(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(self.order_list_url, {'offer_detail_id': self.offer_detail.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Order.objects.count(), 3)

        new_order = Order.objects.latest('id')

        self.assertEqual(new_order.customer_user, self.customer)
        self.assertEqual(new_order.business_user, self.business)
        self.assertEqual(new_order.offer_detail, self.offer_detail)
        self.assertEqual(new_order.price, self.offer_detail.price)
        self.assertEqual(new_order.status, Order.OrderStatus.IN_PROGRESS)

        self.assertEqual(response.data['title'], 'Basic Design')
        self.assertEqual(response.data['business_user'], self.business.id)

    def test_create_order_as_business_user(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.post(self.order_list_url, {'offer_detail_id': self.offer_detail.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_without_offer_detail(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(self.order_list_url,{}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_invalid_offer_detail(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(self.order_list_url, {'offer_detail_id': 9999}, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_unauthenticated(self):
        response = self.client.post(self.order_list_url, {'offer_detail_id': self.offer_detail.id},format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    #Tests PATCH orders ID
    def test_update_order_status_success(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.patch(self.order_detail_url,{'status': Order.OrderStatus.COMPLETED}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.OrderStatus.COMPLETED)

    def test_update_order_as_customer_forbidden(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.patch(self.order_detail_url,{'status': Order.OrderStatus.COMPLETED},format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_order_as_wrong_business_user(self):
        self.client.force_authenticate(user=self.business2)

        response = self.client.patch(self.order_detail_url, {'status': Order.OrderStatus.COMPLETED}, format='json')
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN) #Anpassung an Model

    def test_update_order_with_invalid_status(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.patch(self.order_detail_url, {'status': 'invalid_status'}, format='json')

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

    def test_update_order_unauthenticated(self):
        response = self.client.patch(self.order_detail_url, {'status': Order.OrderStatus.COMPLETED}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    #Test GET order-count {business_user_id}
    def test_get_order_count_success(self):
        self.client.force_authenticate(user=self.customer)

        url = reverse('order-count', kwargs={'business_user_id': self.business.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 1)

    #Test GET completed-order-count {business_user_id}
    def test_get_completed_order_count_success(self):
        Order.objects.create(
            offer_detail=self.offer_detail,
            customer_user=self.customer,
            business_user=self.business,
            title=self.offer_detail.title,
            revisions=self.offer_detail.revisions,
            delivery_time_in_days=self.offer_detail.delivery_time_in_days,
            price=self.offer_detail.price,
            features=self.offer_detail.features,
            offer_type=self.offer_detail.offer_type,
            status=Order.OrderStatus.COMPLETED
        )

        self.client.force_authenticate(user=self.customer)

        url = reverse('completed-order-count',kwargs={'business_user_id': self.business.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 1)

    def test_get_order_count_invalid_business_user(self):
        self.client.force_authenticate(user=self.customer)

        url = reverse('order-count', kwargs={'business_user_id': self.customer.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)