from app.internal.config import settings
from app.utils.constants.settings import App
from jaanca_chronometer import Chronometer
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString

asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))
chronometer=Chronometer()

# Example 1 - Small file
# Container root path
file='upload.txt'
chronometer.start()
url=asabm.container_blob_get_url_sas_read_to_download(file,App.AzureStorageAccount.Containers.NAME_WITH_DATA,expiry_days=1)
chronometer.stop()
if url is False:
    print("There is an error or the blob file does not exist")
else:
    print(f"url: {url}")
    print(f"Elapsed time: {chronometer.get_elapsed_time()}")

# Example 2 - Small file
# Container and subfolders path
container_folders=["folder1","folder2"]
file='upload.txt'
chronometer.start()
url=asabm.container_blob_get_url_sas_read_to_download(file,App.AzureStorageAccount.Containers.NAME_WITH_DATA,container_folders,expiry_days=1)
chronometer.stop()
if url is False:
    print("There is an error or the blob file does not exist")
else:
    print(f"url: {url}")
    print(f"Elapsed time: {chronometer.get_elapsed_time()}")

