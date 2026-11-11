from django.conf import settings
from django.db import models


def profile_image_upload_path(instance, filename):
    return f"profile_images/{instance.user.id}/{filename}"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")

    file = models.FileField(upload_to=profile_image_upload_path, blank=True, null=True)

    location = models.CharField(max_length=255, blank=True, default="")

    tel = models.CharField(max_length=30, blank=True, default="") # wird für den Rückgabewert str: "" gebraucht

    description = models.TextField(blank=True, default="")

    working_hours = models.CharField(max_length=100, blank=True, default="")

    uploaded_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
