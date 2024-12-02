from django.urls import path
from .views import FlightList

urlpatterns = [
    path('flights/', FlightList.as_view(), name='flight-list'),
]