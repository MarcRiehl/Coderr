from django.db import models
from django.conf import settings


class Offer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="offers") # muss business besitzen
    title = models.CharField(max_length=255)
    image = models.CharField(max_length=255, blank=True, null=True) #uploadpfad noch prüfen, null erlauben
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class OfferDetail(models.Model):

    class OfferType(models.TextChoices):
        BASIC = "basic", "Basic"
        STANDARD = "standard", "Standard"
        PREMIUM = "premium", "Premium"

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="details")
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField(blank=True, null=True)
    delivery_time_in_days = models.PositiveIntegerField() #nur positive Zahlen
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20, choices=OfferType.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["offer", "offer_type"],
                name="unique_offer_detail_type"
            )
        ] #UniqueConstrain verhindert doppelte Pakettypen innerhalb desselben Angebots

    def __str__(self):
        return f"{self.offer.title} - {self.get_offer_type_display()}"