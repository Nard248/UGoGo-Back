from django.urls import path
from .views import (
    UserRequestListView,
    CreateRequestView,
    ConfirmStripeSessionView,
    FlightRequestActionView,
    GetPickupCodeView,
    ValidatePickupCodeView,
    GetDeliveryCodeView,
    ValidateDeliveryCodeView,

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

    # STAGE 1: Sender to Courier
    path('my-pickup-code/<int:request_id>/', GetPickupCodeView.as_view(), name='get-pickup-code'),
    path('validate-pickup-code/', ValidatePickupCodeView.as_view(), name='validate-pickup-code'),

    # STAGE 2: Courier to Pickup Person
    path('my-delivery-code/<int:request_id>/', GetDeliveryCodeView.as_view(), name='get-delivery-code'),
    path('validate-delivery-code/', ValidateDeliveryCodeView.as_view(), name='validate-delivery-code'),
]
