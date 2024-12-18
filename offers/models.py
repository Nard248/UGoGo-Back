from django.db import models
from users.models import Users


class Flight(models.Model):
    date = models.DateField()
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)

    def __str__(self):
        return f"Flight {self.origin} to {self.destination} on {self.date}"


class Offer(models.Model):
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='sent_offers')
    courier = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='courier_offers')
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    status = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Offer {self.id} - Status: {self.status}"
