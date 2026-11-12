from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OfferDetailsView, OfferViewSet

router = DefaultRouter()
router.register(r'offers', OfferViewSet, basename='offers')

urlpatterns = [
    path('offerdetails/<int:pk>/', OfferDetailsView.as_view(),
         name='offer-detail-detail'),
    path('', include(router.urls)),
]
