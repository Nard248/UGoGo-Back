from django.urls import path
from items.views import (
    ItemListCreateAPIView,
    ItemDestroyAPIView,
    RequestListCreateAPIView,
    RequestUpdateStatusAPIView,
    RequestDestroyAPIView,
    UnifiedItemCreateView, GetAllCategoriesView
)

urlpatterns = [
    # Item endpoints
    path('items/', ItemListCreateAPIView.as_view(), name='item-list-create'),
    path('items/<int:pk>/', ItemDestroyAPIView.as_view(), name='item-destroy'),

    # Request endpoints
    path('requests/', RequestListCreateAPIView.as_view(), name='request-list-create'),
    path('requests/<int:pk>/', RequestUpdateStatusAPIView.as_view(), name='request-update-status'),
    path('requests/<int:pk>/delete/', RequestDestroyAPIView.as_view(), name='request-destroy'),

    # Unified creation
    path('items/unified_create/', UnifiedItemCreateView.as_view(), name='unified-create-item'),
    path('get_all_categories/', GetAllCategoriesView.as_view(), name='get-all-categories'),
]
