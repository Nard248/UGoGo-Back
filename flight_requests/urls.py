from django.urls import path
from .views import (
    UserRequestListView,
    CreateRequestView,
    ConfirmStripeSessionView,
    FlightRequestActionView
    
)

urlpatterns = [
    # Request Management
    path('list-requests/', UserRequestListView.as_view(), name='request-list'),
    path('create/', CreateRequestView.as_view(), name='request-create'),
    # path('requests/<int:pk>/', RequestUpdateStatusAPIView.as_view(), name='request-get-by-id'),
    path('action/', FlightRequestActionView.as_view(), name='request-update'),  # Accept/reject

    # Stripe Payment Handling
    path('stripe/confirm-session/', ConfirmStripeSessionView.as_view(), name='confirm-stripe-session'),
    # path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook')
]
