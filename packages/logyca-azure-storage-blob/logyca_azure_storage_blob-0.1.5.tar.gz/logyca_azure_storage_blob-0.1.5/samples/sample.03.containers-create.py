from app.internal.config import settings
from app.utils.constants.settings import App
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString

print("\n\n")
asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))
status=asabm.container_create(App.AzureStorageAccount.Containers.NAME_TO_CREATE_DELETE)
if status is True:
    print("Contenedor {} creado...".format(App.AzureStorageAccount.Containers.NAME_TO_CREATE_DELETE))
else:
    print(f"Error: {status}")

status=asabm.container_create(App.AzureStorageAccount.Containers.NAME_WITH_DATA)
if status is True:
    print("Contenedor {} creado...".format(App.AzureStorageAccount.Containers.NAME_WITH_DATA))
else:
    print(f"Error: {status}")

status=asabm.container_create(App.AzureStorageAccount.Containers.NAME_PUBLIC_TO_CREATE_DELETE,"blob")
if status is True:
    print("Contenedor {} creado...".format(App.AzureStorageAccount.Containers.NAME_PUBLIC_TO_CREATE_DELETE))
else:
    print(f"Error: {status}")
