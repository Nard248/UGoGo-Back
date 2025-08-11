from django.conf import settings
from django.db import models

from items.models.items import Item
from offers.models import Offer


class Request(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('in_process', 'In_process'),
        ('in_transit', 'In_transit'),
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # STAGE 1: Sender to Courier verification
    pickup_verification_code = models.CharField(max_length=4, blank=True, null=True)
    pickup_code_generated_at = models.DateTimeField(blank=True, null=True)
    pickup_code_verified = models.BooleanField(default=False)
    pickup_code_verified_at = models.DateTimeField(blank=True, null=True)
    pickup_verification_attempts = models.PositiveIntegerField(default=0)

    # STAGE 2: Courier to Pickup Person verification
    delivery_verification_code = models.CharField(max_length=4, blank=True, null=True)
    delivery_code_generated_at = models.DateTimeField(blank=True, null=True)
    delivery_code_verified = models.BooleanField(default=False)
    delivery_code_verified_at = models.DateTimeField(blank=True, null=True)
    delivery_verification_attempts = models.PositiveIntegerField(default=0)

    # Tracking
    max_verification_attempts = models.PositiveIntegerField(default=3)

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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Request #{self.request.pk} (Status: {self.status})"
