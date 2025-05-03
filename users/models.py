from datetime import datetime, timedelta
from random import randint

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Users(AbstractBaseUser, PermissionsMixin):
    PASSPORT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("rejected", "Rejected")
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    is_passport_uploaded = models.BooleanField(default=False, null=True)
    passport_verification_status = models.CharField(
        max_length=10, choices=PASSPORT_STATUS_CHOICES, default='pending'
    )

    ### email verification
    is_email_verified = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=6, blank=True, null=True)
    code_expiration = models.DateTimeField(blank=True, null=True)

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = "users"  # Ensure table name matches

    def generate_verification_code(self):
        self.email_verification_code = str(randint(100000, 999999))
        self.code_expiration = datetime.now() + timedelta(minutes=10)
        self.save()

    def get_password(self):
        return self.password

    def is_admin(self):
        return self.is_staff

    def set_is_passport_uploaded(self, value):
        self.is_passport_uploaded = value
        self.save()

    def set_passport_verification_status(self, value):
        self.passport_verification_status = value
        self.save()

    def set_is_account_active(self, value):
        self.is_active = value
        self.save()

    @classmethod
    def get_user_by_id(cls, user_id):
        try:
            return cls.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return None


from django.db import models


class PID(models.Model):
    PID_TYPE_CHOICES = [
        ('national_id', 'National ID'),
        ('passport', 'Passport'),
    ]
    pid_holder = models.ForeignKey(
        Users,
        related_name='pids',
        on_delete=models.CASCADE
    )
    pid_type = models.CharField(max_length=20, choices=PID_TYPE_CHOICES)
    pid_picture = models.ImageField(upload_to='pid_pictures/')
    pid_selfie = models.ImageField(upload_to='pid_selfies/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    expiration_date = models.DateField(default=datetime.now() + timedelta(days=30))

    def __str__(self):
        return f"PID Type: {self.pid_type}, Verified: {self.is_verified}"
