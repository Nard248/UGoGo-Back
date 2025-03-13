from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.conf import settings


class ItemCategory(models.Model):
    name = models.CharField(max_length=255)
    icon_path = models.CharField(max_length=255, null=False, default='default_icon.svg')
    description = models.TextField()

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description
        }


class Item(models.Model):
    """
    Represents an item that a sender wants to transport.
    """
    STATE_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    VERIFICATION_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='items',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    dimensions = models.CharField(max_length=100)
    is_pictures_uploaded = models.BooleanField(default=False)
    verified = models.CharField(
        max_length=20,
        choices=VERIFICATION_CHOICES,
        default='pending'
    )
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default='draft'
    )

    categories = models.ManyToManyField(
        'ItemCategory',
        related_name='items',
        blank=True
    )

    pickup_name = models.CharField(max_length=100, blank=True, null=True)
    pickup_surname = models.CharField(max_length=100, blank=True, null=True)
    pickup_phone = models.CharField(max_length=50, blank=True, null=True)
    pickup_email = models.EmailField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Owner: {self.user.email})"

    @classmethod
    def get_item_by_id(cls, item_id):
        try:
            return cls.objects.get(id=item_id)
        except ObjectDoesNotExist:
            return None

    def set_verification_status(self, value):
        self.verified = value
        self.save()

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
