from enum import StrEnum

class App:
    class AzureStorageAccount:
        class Containers(StrEnum):
            NAME_TO_CREATE_DELETE="testlib"
            NAME_PUBLIC_TO_CREATE_DELETE="testlibpublic"
            NAME_WITH_DATA="tmp"