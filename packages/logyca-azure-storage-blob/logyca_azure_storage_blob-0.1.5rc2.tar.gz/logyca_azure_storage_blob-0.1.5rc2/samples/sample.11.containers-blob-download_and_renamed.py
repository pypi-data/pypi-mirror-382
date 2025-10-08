from app.internal.config import settings
from app.utils.constants.settings import App
from jaanca_chronometer import Chronometer
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString
import os

asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))
chronometer=Chronometer()

# Example 1 - Small file
# Container root path
folder_local_full_path=os.path.abspath(os.path.join(os.path.dirname(__file__),'files_download'))
file='upload.txt'
chronometer.start()
status=asabm.container_blob_download_data_transfer_options(folder_local_full_path,file,App.AzureStorageAccount.Containers.NAME_WITH_DATA,max_concurrency=2,verify_file_integrity=True)
chronometer.stop()
if status is True:
    print("blob:[{}] downloaded...".format(os.path.join(folder_local_full_path,file)))
    print(f"Elapsed time: {chronometer.get_elapsed_time()}")
else:
    print(status)

# Example 2 - Small file
# Container and subfolders path
folder_local_full_path=os.path.abspath(os.path.join(os.path.dirname(__file__),'files_download'))
container_folders=["folder1","folder2"]
file='upload.txt'
chronometer.start()
status=asabm.container_blob_download_data_transfer_options(folder_local_full_path,file,App.AzureStorageAccount.Containers.NAME_WITH_DATA,container_folders,max_concurrency=2,verify_file_integrity=True)
chronometer.stop()
if status is True:
    print("blob:[{}] downloaded...".format(os.path.join(folder_local_full_path,file)))
    print(f"Elapsed time: {chronometer.get_elapsed_time()}")
else:
    print(status)

# # Example 3 - Big file
# folder_local_full_path="c:\\tmp"
# file="20240126084440-backup.dump" # 2 GB
# file="video1.mp4" # 4 MB
# # file="video3.mp4" # 1 GB
# chronometer.start()
# status=asabm.container_blob_download_data_transfer_options(folder_local_full_path,file,App.AzureStorageAccount.Containers.NAME_WITH_DATA,max_concurrency=2)
# chronometer.stop()
# if status is True:
#     print("blob:[{}] downloaded...".format(os.path.join(folder_local_full_path,file)))
#     print(f"Elapsed time: {chronometer.get_elapsed_time()}")
# else:
#     print(status)

# Example 4 - Renaming file
# Container and subfolders path
folder_local_full_path=os.path.abspath(os.path.join(os.path.dirname(__file__),'files_download'))
container_folders=["folder1","folder2"]
file='upload.txt'
file_new_name='upload_new_name.txt'
chronometer.start()
status=asabm.container_blob_download_data_transfer_options(folder_local_full_path,file,App.AzureStorageAccount.Containers.NAME_WITH_DATA,container_folders,max_concurrency=2,verify_file_integrity=True,file_new_name=file_new_name)
chronometer.stop()
if status is True:
    print("blob:[{}] downloaded...".format(os.path.join(folder_local_full_path,file)))
    print(f"Elapsed time: {chronometer.get_elapsed_time()}")
else:
    print(status)
