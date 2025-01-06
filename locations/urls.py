# locations/urls.py

from django.urls import path
from .views import (
    CountryListCreateView, CountryDetailView,
    CityListCreateView, CityDetailView,
    AirportListCreateView, AirportDetailView,
    CityPolicyListCreateView, CityPolicyDetailView
)

urlpatterns = [
    # Country Endpoints
    path('countries/', CountryListCreateView.as_view(), name='country-list-create'),
    path('countries/<int:pk>/', CountryDetailView.as_view(), name='country-detail'),

    # City Endpoints
    path('cities/', CityListCreateView.as_view(), name='city-list-create'),
    path('cities/<int:pk>/', CityDetailView.as_view(), name='city-detail'),

    # Airport Endpoints
    path('airports/', AirportListCreateView.as_view(), name='airport-list-create'),
    path('airports/<int:pk>/', AirportDetailView.as_view(), name='airport-detail'),

    # CityPolicy Endpoints
    path('city-policies/', CityPolicyListCreateView.as_view(), name='citypolicy-list-create'),
    path('city-policies/<int:pk>/', CityPolicyDetailView.as_view(), name='citypolicy-detail'),
]
