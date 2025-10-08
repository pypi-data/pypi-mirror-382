from app.internal.config import settings
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString
import json

asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))
data=asabm.get_account_information()
print(json.dumps(data,indent=4))
    # {
    #     "account_kind": "StorageV2",
    #     "client_request_id": "bdae1607-0d7b-11ef-8510-a4b1c13ee715",
    #     "date": "2024-05-08 20:44:19+00:00",
    #     "is_hns_enabled": false,
    #     "request_id": "f771fc3b-901e-003e-5188-a10019000000",
    #     "sku_name": "Standard_LRS",
    #     "version": "2022-11-02"
    # }

