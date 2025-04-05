from azure.storage.blob import BlobServiceClient
from django.conf import settings
import uuid

def upload_file_to_azure(file, container_name=None):
    if not file:
        raise ValueError("No file provided for upload")

    file_name = f"{uuid.uuid4()}_{file.name}"
    container_name = container_name or settings.AZURE_CONTAINERS

    blob_service_client = BlobServiceClient.from_connection_string(
        f"DefaultEndpointsProtocol=https;AccountName={settings.AZURE_ACCOUNT_NAME};AccountKey={settings.AZURE_STORAGE_ACCOUNT_KEY};EndpointSuffix=core.windows.net"
    )
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)

    blob_client.upload_blob(file.read(), overwrite=True)

    return f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{container_name}/{file_name}"
