# booking/models.py
from django.conf import settings
from django.db import models


class Ticket(models.Model):
    picture = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Refer to the custom user model
        on_delete=models.CASCADE,
        related_name='tickets'
    )

    def __str__(self):
        return f"Ticket {self.id} for User {self.user.id}"


class Flight(models.Model):
    date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Refer to the custom user model
        on_delete=models.CASCADE,
        related_name='flights'
    )
    origin = models.CharField(max_length=255, null=True, blank=True)
    destination = models.CharField(max_length=255, null=True, blank=True)
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='flights',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Flight {self.id} from {self.origin} to {self.destination}"


class Offer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Refer to the custom user model
        on_delete=models.CASCADE,
        related_name='sent_offers'
    )
    courier = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Refer to the custom user model
        on_delete=models.CASCADE,
        related_name='courier_offers',
        null=True,
        blank=True
    )
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='offers')
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='pending')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Offer {self.id} - Status: {self.status} - Price: {self.price}"

    class Meta:
        indexes = [
            models.Index(fields=['sender']),  # Index for sender
        ]
