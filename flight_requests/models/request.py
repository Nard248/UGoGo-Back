from django.conf import settings
from django.db import models

from items.models.items import Item
from offers.models import Offer


class Request(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
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
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_requests',
        on_delete=models.CASCADE
    )

    comments = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Request #{self.pk} (Item: {self.item.name}, Offer: {self.offer.id}, Status: {self.status})"

class RequestPayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    request = models.OneToOneField(
        Request,
        related_name='payment',
        on_delete=models.CASCADE
    )
    payment_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Request.STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Request #{self.request.pk} (Status: {self.status})"
