from azure.storage.blob import BlobServiceClient

account_name = "ugogostorageaccount"
account_key = "OzYwtxC4bkYddPUKGNX9tTxvAnwZUupkeXcYfQAaB/VvLeXw5TBdlGOnhZn34wjnbfUg8O+cEQTO+AStXUOuhA=="

try:
    service = BlobServiceClient(
        account_url=f"https://{account_name}.blob.core.windows.net/",
        credential=account_key
    )

    # This will actually send a request to Azure and trigger real auth
    containers = list(service.list_containers())
    print("✅ Authenticated successfully")
    print("Available containers:", [c["name"] for c in containers])

except Exception as e:
    print("❌ Authentication failed:", e)
