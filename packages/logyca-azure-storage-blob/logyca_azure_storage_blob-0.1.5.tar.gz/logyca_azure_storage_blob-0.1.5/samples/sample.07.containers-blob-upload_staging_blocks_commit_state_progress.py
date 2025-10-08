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
file='upload.txt'
chronometer.start()
status=asabm.container_blob_upload_staging_blocks_commit(folder_local_full_path,file,App.AzureStorageAccount.Containers.NAME_WITH_DATA,verify_file_integrity=True,print_charge_percentage=True)
chronometer.stop()
if status is True:
    print("blob:[{}] uploaded...".format(os.path.join(folder_local_full_path,file)))
    print(f"Elapsed time: {chronometer.get_elapsed_time()}")
else:
    print(status)

# Example 2 - Small file
# Container and subfolders path
container_folders=["folder1","folder2"]
file='upload.txt'
chronometer.start()
status=asabm.container_blob_upload_staging_blocks_commit(folder_local_full_path,file,App.AzureStorageAccount.Containers.NAME_WITH_DATA,container_folders,verify_file_integrity=True,print_charge_percentage=True)
chronometer.stop()
if status is True:
    print("folders container:{}, blob:[{}] uploaded...".format(container_folders,os.path.join(folder_local_full_path,file)))
    print(f"Elapsed time: {chronometer.get_elapsed_time()}")
else:
    print(status)

# # Example 3 - Big file
# folder="c:\\tmp"
# file="20240126084440-backup.dump" # 2 GB
# file="video1.mp4" # 4 MB
# # file="video2.mp4" # 1 GB

# chronometer.start()
# status=asabm.container_blob_upload_staging_blocks_commit(folder,file,App.AzureStorageAccount.Containers.NAME_WITH_DATA,print_charge_percentage=True)
# chronometer.stop()
# if status is True:
#     print("blob:[{}] uploaded...".format(os.path.join(folder,file)))
#     print(f"Elapsed time: {chronometer.get_elapsed_time()}")
# else:
#     print(status)

