# locations/models.py

from django.db import models

class Country(models.Model):
    country_code = models.CharField(max_length=10, unique=True)
    country_abbr = models.CharField(max_length=10, unique=True)
    country_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.country_name


class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')
    city_code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    city_abbr = models.CharField(max_length=10, unique=True, null=True, blank=True)
    city_name = models.CharField(max_length=255, unique=True)
    timezone = models.CharField(max_length=50)

    def __str__(self):
        return self.city_name


class Airport(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='airports')
    airport_code = models.CharField(max_length=10, unique=True)
    airport_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.airport_name} ({self.airport_code})"


class CityPolicy(models.Model):
    POLICY_TYPE_CHOICES = [
        ('allowed_categories', 'Allowed Categories'),
        ('restricted_items', 'Restricted Items'),
        # Add more policy types as needed
    ]

    POLICY_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        # Add more statuses as needed
    ]

    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='policies')
    policy_type = models.CharField(max_length=50, choices=POLICY_TYPE_CHOICES)
    policy_status = models.CharField(max_length=20, choices=POLICY_STATUS_CHOICES)
    policy_description = models.TextField()

    def __str__(self):
        return f"{self.city.city_name} - {self.policy_type} ({self.policy_status})"