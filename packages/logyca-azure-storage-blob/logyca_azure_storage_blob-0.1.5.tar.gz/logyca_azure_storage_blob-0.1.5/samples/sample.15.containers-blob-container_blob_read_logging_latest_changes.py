from app.internal.config import settings
from app.utils.constants.settings import App
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString

asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))

# Container root path
file="app_worker.error.log"
container_folders=["logs"]
status=asabm.container_blob_read_logging_latest_changes(App.AzureStorageAccount.Containers.NAME_WITH_DATA,file,container_folders)
if status is True:
    print("blob file message: uploaded...")
else:
    print(status)

