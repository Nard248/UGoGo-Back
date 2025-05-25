import stripe

# Set your Stripe TEST secret key
stripe.api_key = "sk_test_51R81HEQLU3iCaOMisS0uyjCjDGdEaKRKX0tDTC79dQgHoPORR5988ZHdH9nqgehwItqzUVVnHzXgOCzk8wEQv1ai00qv65ADrD"

# === STEP 1: Create Express Connected Account ===
account = stripe.Account.create(
    type="express",
    country="US",
    email="user@example.com",
    capabilities={
        "transfers": {"requested": True}
    },
    business_profile={
        "product_description": "Freelance payouts",
        "mcc": "7299",  # Misc Personal Services
    }
)
print("✅ Connected Express account created:", account.id)

# === STEP 2: Create Account Link for Onboarding ===
account_link = stripe.AccountLink.create(
    account=account.id,
    refresh_url="https://example.com/",
    return_url="https://example.com/",
    type="account_onboarding"
)
print("🔗 Onboarding Link (open in browser):", account_link.url)

# === Optional: After user finishes onboarding ===
# Retrieve account to check verification status
retrieved = stripe.Account.retrieve(account.id)
print("🧾 Current Requirements:", retrieved.requirements)

stripe.Transfer.create(
    amount=5000,  # $50.00
    currency="usd",
    destination=account.id
)