from django.db import models
from users.models import Users

class Item(models.Model):
    weight = models.PositiveIntegerField()
    volume = models.PositiveIntegerField()
    user = models.ForeignKey(Users, on_delete=models.CASCADE)

    def __str__(self):
        return f"Item {self.id} (Weight: {self.weight}, Volume: {self.volume})"
