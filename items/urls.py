from django.urls import path
from items.base_views import (
    ItemListCreateAPIView,
    ItemDestroyAPIView,
    GetAllCategoriesView
)

from items.views.verify_item import VerifyItemView
from items.views.create_item import UnifiedItemCreateView

urlpatterns = [
    # Item endpoints
    path('items/', ItemListCreateAPIView.as_view(), name='item-list-create'),
    path('items/<int:pk>/', ItemDestroyAPIView.as_view(), name='item-destroy'),

    path('create_item/', UnifiedItemCreateView.as_view(), name='unified-create-item'),
    path('get_all_categories/', GetAllCategoriesView.as_view(), name='get-all-categories'),

    path('admin/verify-user-item/', VerifyItemView.as_view(), name='forgot-password'),
]
