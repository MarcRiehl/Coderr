from django.db import models
from django.conf import settings
from offers_app.models import OfferDetail


class Order(models.Model):

    class OrderStatus(models.TextChoices):
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    customer_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_orders") #später für user.customer_orders.all()
    business_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="business_orders") #user.business_orders.all()

    offer_detail = models.ForeignKey(OfferDetail, on_delete=models.PROTECT, related_name="orders") #Aus dem Offerdetail übernehmen, damit nicht doppelt

    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField(null=True,blank=True)
    delivery_time_in_days = models.PositiveIntegerField() #nur positive Zahlen
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20,choices=OfferDetail.OfferType.choices) #OfferType siehe offer_detail

    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.IN_PROGRESS)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.title}"