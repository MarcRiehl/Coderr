from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    class UserType(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        BUSINESS = "business", "Business"

    type = models.CharField(max_length=20, choices=UserType.choices,default=UserType.CUSTOMER)
