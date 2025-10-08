from app.internal.config import settings
from app.utils.constants.settings import App
from jaanca_datetime import DateTimeHelper, App as DateTimeHelperApp
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString, LoggingLevels

asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))

date_now_prefix=DateTimeHelper.get_datetime_now(DateTimeHelperApp.Time.STANDARD_FORMAT_DATE)
print(f"date now: {date_now_prefix}")

# Example 1 - INFO
# Container root path
preffix_name="app_worker"
message = "text text...\ntext text...\ntext text...\ntext text...\n"
status=asabm.container_blob_upload_logging(App.AzureStorageAccount.Containers.NAME_WITH_DATA,LoggingLevels.INFO,preffix_name,message,date_now_prefix)
if status is True:
    print("blob file message: uploaded...")
else:
    print(status)

# Example 1 - ERROR
# Container and subfolders path
preffix_name="app_worker"
container_folders=["logs"]
message = """text text...
text text...
text text...
text text...
"""
status=asabm.container_blob_upload_logging(App.AzureStorageAccount.Containers.NAME_WITH_DATA,LoggingLevels.ERROR,preffix_name,message,date_now_prefix,container_folders)
if status is True:
    print("blob file message: uploaded...")
else:
    print(status)

