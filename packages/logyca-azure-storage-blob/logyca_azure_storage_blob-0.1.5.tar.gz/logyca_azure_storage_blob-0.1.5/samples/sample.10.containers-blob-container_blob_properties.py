from app.internal.config import settings
from app.utils.constants.settings import App
from azure.storage.blob import BlobProperties
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString

asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))

# Example 1 - Small file
# Container root path
blob_file='upload.txt'
blob_properties:BlobProperties=asabm.container_blob_properties(blob_file,App.AzureStorageAccount.Containers.NAME_WITH_DATA)
if isinstance(blob_properties,BlobProperties):
    print("----------------------")
    print(f"name: {blob_properties.name}")
    print(f"size: {blob_properties.size} bytes")
    print(f"content_md5: {blob_properties.content_settings.content_md5}")
    print(f"last_modified: {blob_properties.last_modified}")
    print(f"blob_type: {blob_properties.blob_type}")
else:
    print(blob_properties)

# Example 2 - Small file
# Container and subfolders path
blob_file='upload.txt'
container_folders=["folder1","folder2"]
blob_properties:BlobProperties=asabm.container_blob_properties(blob_file,App.AzureStorageAccount.Containers.NAME_WITH_DATA,container_folders)
if isinstance(blob_properties,BlobProperties):
    print("----------------------")
    print(f"name: {blob_properties.name}")
    print(f"size: {blob_properties.size} bytes")
    print(f"content_md5: {blob_properties.content_settings.content_md5}")
    print(f"last_modified: {blob_properties.last_modified}")
    print(f"blob_type: {blob_properties.blob_type}")
else:
    print(blob_properties)

# name: upload.txt
# size: 62 bytes
# content_md5: bytearray(b'\xe9tS\xc7\xf7\x87\x9a\xe0T\x9f\x97\xb8B\xa5y\x8d')
# last_modified: 2024-05-15 14:47:08+00:00
# blob_type: BlobType.BLOCKBLOB
# name: folder1/folder2/upload.txt
# size: 62 bytes
# content_md5: bytearray(b'\xe9tS\xc7\xf7\x87\x9a\xe0T\x9f\x97\xb8B\xa5y\x8d')
# last_modified: 2024-05-15 14:46:45+00:00
# blob_type: BlobType.BLOCKBLOB
