from app.internal.config import settings
from app.utils.constants.settings import App
from jaanca_chronometer import Chronometer
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString
import os

asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))
folder_local_full_path=os.path.abspath(os.path.join(os.path.dirname(__file__),'files'))
chronometer=Chronometer()

# Example 1 - Small file
# Container root path
file='video3.mp4'
file='upload.txt'
chronometer.start()
status=asabm.checksum_compare_local_file_versus_remote_content_md5(folder_local_full_path,file,App.AzureStorageAccount.Containers.NAME_WITH_DATA)
chronometer.stop()
if status is True:
    print("blob:[{}] checksum ok...".format(os.path.join(folder_local_full_path,file)))
    print(f"Elapsed time: {chronometer.get_elapsed_time()}")
else:
    print(status)

# Example 2 - Small file
# Container and subfolders path
file='upload.txt'
container_folders=["folder1","folder2"]
chronometer.start()
status=asabm.checksum_compare_local_file_versus_remote_content_md5(folder_local_full_path,file,App.AzureStorageAccount.Containers.NAME_WITH_DATA,container_folders)
chronometer.stop()
if status is True:
    print("blob:[{}]  checksum ok...".format(os.path.join(folder_local_full_path,file)))
    print(f"Elapsed time: {chronometer.get_elapsed_time()}")
else:
    print(status)
