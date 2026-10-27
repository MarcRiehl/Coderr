from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import RetrieveAPIView

class OfferViewSet(ModelViewSet): #	GET, POST, PUT, PATCH, DELETE
    pass

class OfferDetailsView(RetrieveAPIView): #einzelnes Objekt abrufen
    pass