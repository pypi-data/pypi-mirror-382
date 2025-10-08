from enum import StrEnum

class Environment:
    class AzureStorageAccount:
        class AccessKeys(StrEnum):
            ACCOUNT_NAME="AZURESTORAGEACCOUNT_ACCOUNT_NAME"
            ACCOUNT_KEY="AZURESTORAGEACCOUNT_ACCOUNT_KEY"
            CONNECTION_STRING="AZURESTORAGEACCOUNT_CONNECTION_STRING"

