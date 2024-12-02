from django.db import models
from django.contrib.postgres.fields import JSONField  # Use only if PostgreSQL is your DB

class User(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    hashed_password = models.CharField(max_length=255)
    # pid = models.OneToOneField('PID', on_delete=models.SET_NULL, null=True, blank=True, related_name='user')  # Assuming PID is another model
    # ticket_ids = JSONField(null=True, blank=True)  # Requires PostgreSQL; use TextField with JSON serialization for other DBs

    def __str__(self):
        return self.name or f"User {self.id}"
