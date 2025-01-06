from django.contrib import admin
from .models import Flight, UserFlight, Offer

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('id', 'publisher', 'from_airport', 'to_airport', 'departure_datetime', 'arrival_datetime')
    list_filter = ('publisher', 'from_airport', 'to_airport')
    search_fields = ('from_airport__airport_name', 'to_airport__airport_name')

@admin.register(UserFlight)
class UserFlightAdmin(admin.ModelAdmin):
    list_display = ('id', 'flight', 'user', 'publish_datetime')
    list_filter = ('flight', 'user')
    search_fields = ('flight__publisher', 'user__email')

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_flight', 'courier', 'status', 'price', 'available_weight', 'available_space')
    list_filter = ('status', 'courier')
    search_fields = ('user_flight__user__email', 'courier__email')
