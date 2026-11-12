from django.conf import settings
from django.db import models


class Business(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="businesses"
    )
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    country = models.CharField(max_length=100, default="Kenya")
    city = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    currency = models.CharField(max_length=3, default="KES")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
