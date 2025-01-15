from django.db import models
from django.conf import settings


class ItemCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class Item(models.Model):
    """
    Represents an item that a sender wants to transport.
    """
    STATE_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
        # Add more states as needed
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='items',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)  # optional
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    dimensions = models.CharField(max_length=100)  # e.g., "15x10x2"
    verified = models.BooleanField(default=False)  # can be changed by admin or left open
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default='draft'
    )

    # M2M with categories (instead of a single FK)
    categories = models.ManyToManyField(
        'ItemCategory',
        related_name='items',
        blank=True
    )

    # Pick-up Person Info
    pickup_name = models.CharField(max_length=100, blank=True, null=True)
    pickup_surname = models.CharField(max_length=100, blank=True, null=True)
    pickup_phone = models.CharField(max_length=50, blank=True, null=True)
    pickup_email = models.EmailField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Owner: {self.user.email})"


class ItemPicture(models.Model):
    """
    Multiple pictures for a single item.
    """
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='pictures'
    )
    image_path = models.CharField(max_length=255)

    def __str__(self):
        return f"Picture for {self.item.name}: {self.image_path}"
