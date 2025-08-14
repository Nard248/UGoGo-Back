from django.urls import path
from .views import (
    UserRequestListView,
    CreateRequestView,
    ConfirmStripeSessionView,
    FlightRequestActionView,
    MySentRequestsView
)

urlpatterns = [
    # Request Management
    path('received/', UserRequestListView.as_view(), name='requests-received'),  # Requests received by courier
    path('sent/', MySentRequestsView.as_view(), name='my-sent-requests'),
    path('create/', CreateRequestView.as_view(), name='request-create'),
    path('action/', FlightRequestActionView.as_view(), name='request-update'),  # Accept/reject

    # Stripe Payment Handling
    path('stripe/confirm-session/', ConfirmStripeSessionView.as_view(), name='confirm-stripe-session'),
]