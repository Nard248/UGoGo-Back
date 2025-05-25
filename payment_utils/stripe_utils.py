import stripe
from ugogo.settings import STRIPE_SECRET_KEY

# Setup Stripe API key
stripe.api_key = STRIPE_SECRET_KEY

def create_connected_account(country='US', email=None):
    """
    Create a Stripe Custom-connected account.
    """
    try:
        account = stripe.Account.create(
            type="custom",
            country=country,
            email=email,
            capabilities={"transfers": {"requested": True}},
        )
        return account
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe account creation failed: {e.user_message}")


def attach_bank_account(account_id, token):
    """
    Attach a user's bank account or debit card to their Stripe Custom account.
    'token' is typically generated using Stripe Elements or Stripe.js on the frontend.
    """
    try:
        external_account = stripe.Account.create_external_account(
            account_id,
            external_account=token
        )
        return external_account
    except stripe.error.StripeError as e:
        raise Exception(f"Attaching bank account failed: {e.user_message}")


def update_account_verification(account_id, individual_info, tos_acceptance):
    """
    Update the Stripe connected account with required verification details.
    'individual_info' and 'tos_acceptance' are dicts with user information.
    """
    try:
        account = stripe.Account.modify(
            account_id,
            individual=individual_info,
            tos_acceptance=tos_acceptance
        )
        return account
    except stripe.error.StripeError as e:
        raise Exception(f"Updating account verification failed: {e.user_message}")


def transfer_to_connected_account(account_id, amount, currency='usd'):
    """
    Transfer funds from your platform balance to the connected account.
    Amount should be provided in cents.
    """
    try:
        transfer = stripe.Transfer.create(
            amount=amount,
            currency=currency,
            destination=account_id,
        )
        return transfer
    except stripe.error.StripeError as e:
        raise Exception(f"Transfer failed: {e.user_message}")


def payout_to_user(account_id, amount, currency='usd', method='standard'):
    """
    Manually trigger payout from connected account to user’s external account.
    Amount should be in cents.
    'method' can be 'standard' or 'instant' if eligible.
    """
    try:
        payout = stripe.Payout.create(
            amount=amount,
            currency=currency,
            method=method,
            stripe_account=account_id
        )
        return payout
    except stripe.error.StripeError as e:
        raise Exception(f"Payout failed: {e.user_message}")


def get_account_requirements(account_id):
    """
    Retrieve verification requirements for connected accounts.
    """
    try:
        account = stripe.Account.retrieve(account_id)
        return account.requirements
    except stripe.error.StripeError as e:
        raise Exception(f"Retrieving account info failed: {e.user_message}")
