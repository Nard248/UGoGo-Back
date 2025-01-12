from django.conf import settings
from django.db import models


class Item(models.Model):
    """
    Represents an item that a sender wants to transport.
    """
    __tablename__ = 'category'
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='items',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    dimensions = models.CharField(max_length=100)  # e.g., "15x10x2" in centimeters
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey("ItemCategory", on_delete=models.SET_NULL, null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.name} by {self.user.email}"

    class Meta:
        ordering = ['-created_at']


class ItemCategory(models.Model):

    name = models.CharField(max_length=255)
    description = models.TextField()


    def __str__(self):
        return f"{self.name} by {self.user.email}"
