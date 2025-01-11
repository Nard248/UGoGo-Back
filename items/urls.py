from django.urls import path
from .views import (
    ItemListCreateAPIView,
    ItemDestroyAPIView,
    RequestCreateAPIView,
    RequestUpdateStatusAPIView,
    RequestDestroyAPIView,
)

urlpatterns = [
    # ---------------------
    # Items
    # ---------------------
    # Test references 'item-list-create'
    path('items/', ItemListCreateAPIView.as_view(), name='item-list-create'),
    # Test references 'item-destroy'
    path('items/<int:pk>/', ItemDestroyAPIView.as_view(), name='item-destroy'),

    # ---------------------
    # Requests
    # ---------------------
    # Test references 'request-create'
    path('requests/', RequestCreateAPIView.as_view(), name='request-create'),
    # Test references 'request-update-status'
    path('requests/<int:pk>/', RequestUpdateStatusAPIView.as_view(), name='request-update-status'),
    # Test references 'request-destroy'
    path('requests/<int:pk>/delete/', RequestDestroyAPIView.as_view(), name='request-destroy'),
]
