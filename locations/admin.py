# locations/admin.py

from django.contrib import admin
from .models import Country, City, Airport, CityPolicy

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'country_code', 'country_abbr', 'country_name')
    search_fields = ('country_code', 'country_abbr', 'country_name')


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'city_code', 'city_abbr', 'city_name', 'country', 'timezone')
    search_fields = ('city_code', 'city_abbr', 'city_name')
    list_filter = ('country', 'timezone')


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('id', 'airport_code', 'airport_name', 'city')
    search_fields = ('airport_code', 'airport_name')
    list_filter = ('city',)


@admin.register(CityPolicy)
class CityPolicyAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'policy_type', 'policy_status')
    search_fields = ('city__city_name', 'policy_type', 'policy_status')
    list_filter = ('policy_type', 'policy_status', 'city')
