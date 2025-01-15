# offers/models.py

from django.db import models
from django.conf import settings
from locations.models import Airport
from items.models.items import ItemCategory


class Flight(models.Model):
    PUBLISHER_CHOICES = [
        ('airline', 'Airline'),
        ('custom', 'Custom Flight'),
    ]

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    publisher = models.CharField(max_length=20, choices=PUBLISHER_CHOICES, default='airline')

    from_airport = models.ForeignKey(Airport, related_name='departing_flights', on_delete=models.CASCADE)
    to_airport = models.ForeignKey(Airport, related_name='arriving_flights', on_delete=models.CASCADE)

    departure_datetime = models.DateTimeField()
    arrival_datetime = models.DateTimeField()

    flight_number = models.CharField(max_length=50, blank=True, default='')

    details = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Flight {self.flight_number} from {self.from_airport} to {self.to_airport}"


class UserFlight(models.Model):
    flight = models.ForeignKey(Flight, related_name='user_flights', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_flights', on_delete=models.CASCADE)
    publish_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"UserFlight {self.id} by {self.user.email}"


class Offer(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('taken', 'Taken'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user_flight = models.ForeignKey(UserFlight, related_name='offers', on_delete=models.CASCADE)
    courier = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='courier_offers', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    categories = models.ManyToManyField(
        ItemCategory,
        blank=True,
        related_name='offers'
    )

    allow_fragile = models.BooleanField(default=False)

    available_dimensions = models.CharField(max_length=100, null=True, blank=True)

    available_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    available_space = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Offer {self.id} by {self.courier.email} - Status: {self.status}"
