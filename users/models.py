from django.db import models


class User(models.Model):
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=50, null=True, blank=True)
    image_id = models.IntegerField(null=True, blank=True)
    hashed_password = models.CharField(max_length=255, default=None)  # Add this field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
