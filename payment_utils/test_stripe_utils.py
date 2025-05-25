import time

import stripe

# Set your Stripe TEST secret key
stripe.api_key = "sk_test_51R81HEQLU3iCaOMisS0uyjCjDGdEaKRKX0tDTC79dQgHoPORR5988ZHdH9nqgehwItqzUVVnHzXgOCzk8wEQv1ai00qv65ADrD"

# Create Custom account (Test Mode)
# account = stripe.Account.create(
#     type="express",
#     country="US",
#     email="user@example.com",
#     business_type="individual",
#     capabilities={
#         "transfers": {"requested": True},
#     },
#     business_profile={
#         "product_description": "Example description",
#         "mcc": "5734",  # Example MCC (Computer Software Stores)
#     },
#     individual={
#         "first_name": "John",
#         "last_name": "Doe",
#         "dob": {"day": 1, "month": 1, "year": 1990},
#         "ssn_last_4": "0000",
#         "email": "user@example.com",
#         "address": {
#             "line1": "123 Main Street",
#             "city": "San Francisco",
#             "state": "CA",
#             "postal_code": "94111",
#             "country": "US",
#         },
#         "phone": "0000000000",
#     },
#     tos_acceptance={
#         "date": int(time.time()),
#         "ip": "192.168.0.1",
#     },
# )
account = stripe.Account.create(
    type="express",
    country="US",
    email="user@example.com",
    capabilities={
        "transfers": {"requested": True}
    }
)
print("Connected Express account:", account.id)

print("Connected account created:", account.id)

# Attach Test Bank Account (Using Stripe's test token)
bank_account = stripe.Account.create_external_account(
    account.id,
    external_account="btok_us_verified"  # Stripe's provided test token
)
print("Bank account attached:", bank_account.id)

# Update Verification Details (Example info)
account_update = stripe.Account.modify(
    account.id,
    business_type="individual",
    individual={
        "first_name": "John",
        "last_name": "Doe",
        "dob": {"day": 1, "month": 1, "year": 1990},
        "ssn_last_4": "0000"
    },
    tos_acceptance={
        "date": 1622548800,
        "ip": "192.168.0.1"
    }
)
print("Verification updated:", account_update.individual.first_name)

# Make a Test Transfer to Connected Account
transfer = stripe.Transfer.create(
    amount=1000,  # $10.00
    currency="usd",
    destination=account.id,
)
print("Transfer made:", transfer.id)

# Create a Test Payout from Connected Account
payout = stripe.Payout.create(
    amount=1000,
    currency="usd",
    stripe_account=account.id,
)
print("Payout initiated:", payout.id)

# Check Account Requirements
retrieved_account = stripe.Account.retrieve(account.id)
print("Current account requirements:", retrieved_account.requirements)
