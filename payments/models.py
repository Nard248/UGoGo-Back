from django.db import models
from users.models import Users
from offers.models import Offer
from items.models.items import Item

class Payment(models.Model):
    status = models.CharField(max_length=255)
    payment_option = models.CharField(max_length=255)
    payer = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='payments_made')
    payee = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='payments_received')
    payer_amount = models.PositiveIntegerField()
    payee_amount = models.PositiveIntegerField()

    def __str__(self):
        return f"Payment {self.id} - Status: {self.status}"


class Request(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    status = models.CharField(max_length=255)

    def __str__(self):
        return f"Request {self.id} - Status: {self.status}"