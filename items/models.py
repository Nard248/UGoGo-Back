# items/models.py

from django.db import models
from django.conf import settings
from offers.models import Offer


class Item(models.Model):
    """
    Represents an item that a sender wants to transport.
    """
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

    def __str__(self):
        return f"{self.name} by {self.user.email}"

    class Meta:
        ordering = ['-created_at']


class Request(models.Model):
    """
    Represents a sender's request to transport an item via a flight offer.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    item = models.ForeignKey(
        Item,
        related_name='requests',
        on_delete=models.CASCADE
    )
    offer = models.ForeignKey(
        Offer,
        related_name='requests',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='requests',
        on_delete=models.CASCADE
    )
    suggested_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request {self.id} by {self.user.email} for Offer {self.offer.id}"

    class Meta:
        ordering = ['-created_at']
