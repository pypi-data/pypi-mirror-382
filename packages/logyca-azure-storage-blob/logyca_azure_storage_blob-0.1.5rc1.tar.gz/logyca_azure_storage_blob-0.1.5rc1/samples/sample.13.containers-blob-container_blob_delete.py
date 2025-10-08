from app.internal.config import settings
from app.utils.constants.settings import App
from jaanca_chronometer import Chronometer
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString
import os

asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))
chronometer=Chronometer()

# Container root path
file='upload.txt'
chronometer.start()
status=asabm.container_blob_delete(file,App.AzureStorageAccount.Containers.NAME_WITH_DATA)
chronometer.stop()
if status is True:
    print("blob:[{}] deleted...".format(os.path.join(file)))
    print(f"Elapsed time: {chronometer.get_elapsed_time()}")
else:
    print(status)

# Subfolders
container_folders=["folder1","folder2"]
file='upload.txt'
chronometer.start()
status=asabm.container_blob_delete(file,App.AzureStorageAccount.Containers.NAME_WITH_DATA,container_folders=container_folders)
chronometer.stop()
if status is True:
    path_blob = "/".join(container_folders + [file])
    print("blob:[{}] deleted...".format(path_blob))
    print(f"Elapsed time: {chronometer.get_elapsed_time()}")
else:
    print(status)

