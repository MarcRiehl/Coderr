from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Review(models.Model):
    business_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_reviews")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name="written_reviews")
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )# Bewertung 1 - 5
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business_user", "reviewer"],
                name="unique_review_per_business_user"
            )
        ] #UniqueConstraint verhindert mehrfache Bewertung
        ordering = ["-updated_at"]

    def __str__(self):
        return (
            f"Review by {self.reviewer} "
            f"for {self.business_user} ({self.rating}/5)"
        )