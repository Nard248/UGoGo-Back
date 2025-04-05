from storages.backends.azure_storage import AzureStorage
from ugogo import settings


class AzureItemImageStorage(AzureStorage):
    account_name = settings.AZURE_ACCOUNT_NAME
    account_key = settings.AZURE_ACCOUNT_KEY
    azure_container = settings.AZURE_ITEM_IMAGE_CONTAINER
    expiration_secs = None

class AzurePassportStorage(AzureStorage):
    account_name = settings.AZURE_ACCOUNT_NAME
    account_key = settings.AZURE_ACCOUNT_KEY
    azure_container = settings.AZURE_USER_PASSPORT_IMAGE_CONTAINER
    expiration_secs = None