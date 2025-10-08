from app.internal.config import settings
from app.utils.constants.settings import App
from azure.storage.blob import BlobProperties
import json
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString

asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))
#################
# root folder
# blob_list=asabm.container_blob_list(App.AzureStorageAccount.Containers.NAME_WITH_DATA,include_subfolders=False)
#################
# subfolders
# container_folders=["logs","logs1"]
# blob_list=asabm.container_blob_list(App.AzureStorageAccount.Containers.NAME_WITH_DATA,container_folders=container_folders)
#################
# modified_hours_ago
container=App.AzureStorageAccount.Containers.NAME_WITH_DATA
container_folders=["folder1","folder1"]
blob_list=asabm.container_blob_list(container,container_folders=container_folders,include_subfolders=False,modified_minutes_ago=2)
for blob in blob_list:
    blob_properties:BlobProperties = blob
    print("----------------------")
    print(f"name: {blob_properties.name}")
    print(f"size: {blob_properties.size} bytes")
    print(f"content_md5: {blob_properties.content_settings.content_md5}")
    print(f"last_modified: {blob_properties.last_modified}")
    print(f"blob_type: {blob_properties.blob_type}")
    # print(json.dumps(blob_properties.__dict__,indent=4,default=str))

    # Folders and subfolders
    # ----------------------
    # name: 20240126084440-backup.backup
    # size: 2186151528 bytes
    # content_md5: bytearray(b'\xcaR7\xc4\x99a\xcf?\xd1\xde\xf2d&\xcc\x15\x08')
    # last_modified: 2024-05-14 21:49:35+00:00
    # blob_type: BlobType.BLOCKBLOB
    # ----------------------
    # name: 20240126084440-backup.dump
    # size: 2186151528 bytes
    # content_md5: bytearray(b'\xcaR7\xc4\x99a\xcf?\xd1\xde\xf2d&\xcc\x15\x08')
    # last_modified: 2024-05-15 01:49:30+00:00
    # blob_type: BlobType.BLOCKBLOB
    # ----------------------
    # name: Doctor Strange - Hechicero Supremo.mp4
    # size: 1127486752 bytes
    # content_md5: None
    # last_modified: 2024-05-15 03:24:38+00:00
    # blob_type: BlobType.BLOCKBLOB
    # ----------------------
    # name: app_worker.info.log
    # size: 216 bytes
    # content_md5: None
    # last_modified: 2024-05-15 04:00:47+00:00
    # blob_type: BlobType.APPENDBLOB
    # ----------------------
    # name: folder1/folder2/upload.txt
    # size: 62 bytes
    # content_md5: bytearray(b'\xe9tS\xc7\xf7\x87\x9a\xe0T\x9f\x97\xb8B\xa5y\x8d')
    # last_modified: 2024-05-15 14:46:45+00:00
    # blob_type: BlobType.BLOCKBLOB
    # ----------------------
    # name: logs/app_worker.error.log
    # size: 216 bytes
    # content_md5: None
    # last_modified: 2024-05-15 04:00:47+00:00
    # blob_type: BlobType.APPENDBLOB
    # ----------------------
    # name: upload.txt
    # size: 62 bytes
    # content_md5: bytearray(b'\xe9tS\xc7\xf7\x87\x9a\xe0T\x9f\x97\xb8B\xa5y\x8d')
    # last_modified: 2024-05-15 14:47:08+00:00
    # blob_type: BlobType.BLOCKBLOB
    # ----------------------
    # name: video1.mp4
    # size: 4869295 bytes
    # content_md5: bytearray(b'-\xd4\xa3\xf6\x80\xb6i\xcddb\xa4z\x9dB=\xee')
    # last_modified: 2024-05-15 02:40:03+00:00
    # blob_type: BlobType.BLOCKBLOB
    # ----------------------
    # name: video3.mp4
    # size: 1127486752 bytes
    # content_md5: None
    # last_modified: 2024-05-15 03:25:32+00:00
    # blob_type: BlobType.BLOCKBLOB