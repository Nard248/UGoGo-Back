# offers/urls.py

from django.urls import path
from .views import (
    FlightListCreateAPIView,
    FlightDetailAPIView,
    FlightSearchAPIView,
    OfferDetailAPIView, OfferListCreateAPIView, UserFlightListCreateAPIView, UserFlightDetailAPIView
)

urlpatterns = [
    path('flights/', FlightListCreateAPIView.as_view(), name='flight-list-create'),
    path('flights/search/', FlightSearchAPIView.as_view(), name='flight-search'),
    path('flights/<int:pk>/', FlightDetailAPIView.as_view(), name='flight-detail'),
    path('offers/', OfferListCreateAPIView.as_view(), name='offer-list-create'),
    path('offers/<int:pk>/', OfferDetailAPIView.as_view(), name='offer-detail'),
    path('userflights/', UserFlightListCreateAPIView.as_view(), name='userflight-list-create'),
    path('userflights/<int:pk>/', UserFlightDetailAPIView.as_view(), name='userflight-detail'),
]

