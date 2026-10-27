from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, ProfileBusinessViewSet, ProfileCustomerViewSet

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = [
    path('profiles/business/', ProfileBusinessViewSet.as_view(), name="profiles-business"),
    path('profiles/customer/', ProfileCustomerViewSet.as_view(), name="profiles-customer"),
    path('', include(router.urls)),
]