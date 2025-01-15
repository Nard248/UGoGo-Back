from django.db import models
from django.conf import settings
from items.models.items import Item
from offers.models import Offer


class Request(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
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
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Request #{self.pk} (Item: {self.item.name}, Offer: {self.offer.id}, Status: {self.status})"
