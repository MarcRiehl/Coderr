from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProfilesBusinessView, ProfilesCustomerView, ProfileViewSet

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = [
    path('profiles/business/', ProfilesBusinessView.as_view(),
         name="profiles-business"),
    path('profiles/customer/', ProfilesCustomerView.as_view(),
         name="profiles-customer"),
    path('', include(router.urls)),
]
