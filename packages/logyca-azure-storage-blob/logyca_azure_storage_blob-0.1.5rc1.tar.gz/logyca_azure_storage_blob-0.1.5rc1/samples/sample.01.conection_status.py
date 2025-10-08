from app.internal.config import settings
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsNameKey, SetCredentialsConnectionString

asabm=AzureStorageAccountBlobManagement(SetCredentialsNameKey(account_name=settings.account_name,key=settings.account_key))
print("SetCredentialsNameKey: Successfully connection") if asabm.get_connect_status() else print("SetCredentialsNameKey: Failed connection")

asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))
print("SetCredentialsNameKey: Successfully connection") if asabm.get_connect_status() else print("SetCredentialsNameKey: Failed connection")
