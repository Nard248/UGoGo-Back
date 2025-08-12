from django.urls import path
from .views import (
    UserRequestListView,
    CreateRequestView,
    ConfirmStripeSessionView,
    FlightRequestActionView,
    MySentRequestsView,
    MyReceivedRequestsView
)

urlpatterns = [
    # Request Management
    path('list-requests/', UserRequestListView.as_view(), name='request-list'),  # Legacy (received requests)
    path('sent/', MySentRequestsView.as_view(), name='my-sent-requests'),
    path('received/', MyReceivedRequestsView.as_view(), name='my-received-requests'),
    path('create/', CreateRequestView.as_view(), name='request-create'),
    path('action/', FlightRequestActionView.as_view(), name='request-update'),  # Accept/reject

    # Stripe Payment Handling
    path('stripe/confirm-session/', ConfirmStripeSessionView.as_view(), name='confirm-stripe-session'),
]