from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CompletedOrderCountView, OrderCountView, OrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('order-count/<int:business_user_id>/',
         OrderCountView.as_view(), name='order-count',),
    path('completed-order-count/<int:business_user_id>/', CompletedOrderCountView.as_view(), name='completed-order-count',
         ),
    path('', include(router.urls)),
]
