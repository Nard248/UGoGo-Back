# offers/models.py

from django.db import models
from users.models import Users
from locations.models import Airport
from items.models.items import ItemCategory


class Flight(models.Model):
    PUBLISHER_CHOICES = [
        ('airline', 'Airline'),
        ('custom', 'Custom Flight'),
    ]

    creator = models.ForeignKey(Users, on_delete=models.CASCADE, default=1)
    publisher = models.CharField(max_length=20, choices=PUBLISHER_CHOICES, default='airline')
    from_airport = models.ForeignKey(Airport, related_name='departing_flights', on_delete=models.CASCADE)
    to_airport = models.ForeignKey(Airport, related_name='arriving_flights', on_delete=models.CASCADE)
    departure_datetime = models.DateTimeField()
    arrival_datetime = models.DateTimeField()
    flight_number = models.CharField(max_length=50, choices=PUBLISHER_CHOICES, default='airline')
    details = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.publisher.capitalize()} Flight from {self.from_airport} to {self.to_airport}"


class UserFlight(models.Model):
    flight = models.ForeignKey(Flight, related_name='user_flights', on_delete=models.CASCADE)
    user = models.ForeignKey(Users, related_name='user_flights', on_delete=models.CASCADE)
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
    courier = models.ForeignKey(Users, related_name='courier_offers', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    allow_fragile = models.BooleanField(default=False)
    available_dimensions = models.CharField(max_length=50, default='0x0x0')
    available_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    available_space = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    categories = models.ManyToManyField(ItemCategory, related_name='offers', blank=True, through='OfferCategory')
    notes = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"Offer {self.id} by {self.courier.email} - Status: {self.status}"

class OfferCategory(models.Model):
    offer = models.ForeignKey('Offer', on_delete=models.CASCADE)
    category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE)