from app.internal.config import settings
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString

asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))
containers=asabm.container_list()
for container in containers:
    print(container.name)

    # [
    #     {'name': 'datos', 
    #         'last_modified': datetime.datetime(2022, 3, 19, 20, 29, 14, tzinfo=datetime.timezone.utc), 
    #         'etag': '"0x8DA09E7226CA6FE"', 
    #         'lease': {
    #             'status': 'unlocked', 
    #             'state': 'available', 
    #             'duration': None}, 
    #             'public_access': None, 
    #             'has_immutability_policy': False, 
    #             'deleted': None, 
    #             'version': None, 
    #             'has_legal_hold': False, 
    #             'metadata': {}, 
    #             'encryption_scope': <azure.storage.blob._models.ContainerEncryptionScope object at 0x000001E338804130>, 
    #             'immutable_storage_with_versioning_enabled': False}, 
    #     {'name': 'other1', 'last_modified': datetime.datetime(2022, 3, 26, 0, 58, 28, tzinfo=datetime.timezone.utc), 'etag': '"0x8DA0EC3BD3E1050"', 'lease': {'status': 'unlocked', 'state': 'available', 'duration': None}, 'public_access': None, 'has_immutability_policy': False, 'deleted': None, 'version': None, 'has_legal_hold': False, 'metadata': {}, 'encryption_scope': <azure.storage.blob._models.ContainerEncryptionScope object at 0x000001E338804D60>, 'immutable_storage_with_versioning_enabled': False}, 
    #     {'name': 'other2', 'last_modified': datetime.datetime(2022, 3, 26, 0, 58, 35, tzinfo=datetime.timezone.utc), 'etag': '"0x8DA0EC3C15E3A9E"', 'lease': {'status': 'unlocked', 'state': 'available', 'duration': None}, 'public_access': None, 'has_immutability_policy': False, 'deleted': None, 'version': None, 'has_legal_hold': False, 'metadata': {}, 'encryption_scope': <azure.storage.blob._models.ContainerEncryptionScope object at 0x000001E338804400>, 'immutable_storage_with_versioning_enabled': False}
    # ]
    # datos
    # other1
    # other2
