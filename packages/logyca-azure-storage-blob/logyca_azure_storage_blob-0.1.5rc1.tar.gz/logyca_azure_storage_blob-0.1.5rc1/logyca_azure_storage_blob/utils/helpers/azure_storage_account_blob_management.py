from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Literal
import datetime, hashlib, json, math, os, re, time, uuid
from azure.storage.blob import (
    BlobBlock,
    BlobClient,
    BlobPrefix,
    BlobProperties,
    BlobSasPermissions,
    BlobServiceClient,
    ContentSettings,
    generate_blob_sas,
    PublicAccess,
    )

class SetCredentialsNameKey:
    '''
    Storage account name + Key
    '''
    def __init__(self,account_name:str,key:str) -> None:
        self.account_name=account_name
        self.key=key

class SetCredentialsConnectionString:
    '''
    Storage account name + Key
    '''
    def __init__(self,connection_string:str) -> None:
        self.connection_string=connection_string

class LoggingLevels(StrEnum):
    CRITICAL = 'critical'
    DEBUG = 'debug'
    ERROR = 'error'
    INFO = 'info'
    WARNING = 'warning'

class AzureStorageAccountBlobManagementErrorCode(StrEnum):
    BLOB_FILE_NOT_FOUND = "Blob file not found."
    CHECKSUM_CONTENT_MD5_NOT_FOUND = "The blob file has no content_md5 checksum."
    CHECKSUM_CONTENT_MD5_VERSUS_NOT_MATCH = "The CHECKSUM content md5 of the local file versus that of the blob file do not match."
    LOCAL_AND_REMOTE_SIZE_DO_NOT_MATCH = "Local and remote size do not match."

class AzureStorageAccountBlobManagement:
    '''Description

    Library with functionalities similar to azcopy where the content_md5 checksum is used to validate the integrity of the file uploaded or downloaded to the blob service.
    
    ## Azcopy command example

    ```console
    azcopy --put-md5
    ```
    '''
    __service_client_conn:BlobServiceClient
    def __init__(self,set_credentials:tuple[SetCredentialsNameKey|SetCredentialsConnectionString]):
        self.__account_name = None
        self.__account_key = None
        self.__account_url = None
        self.__connection_string = None
        self.__chunk_size_bytes=4*1024*1024 # Defaults 4 MiB, The maximum chunk size for uploading a block blob in chunks.
        self.__max_single_put_size=8*1024*1024 # Defaults to 64 MiB. If the blob size is less than or equal to max_single_put_size, the blob is uploaded with a single Put Blob request. If the blob size is larger than max_single_put_size or unknown, the blob is uploaded in chunks using Put Block and committed using Put Block List.
        account_url_template='https://{}.blob.core.windows.net'
        if isinstance(set_credentials,SetCredentialsNameKey):
            setcredentials_name_key:SetCredentialsNameKey=set_credentials
            self.__account_name=setcredentials_name_key.account_name
            self.__account_key=setcredentials_name_key.key
            account_url=account_url_template.format(self.__account_name)
            self.__account_url=account_url
            self.__service_client_conn = BlobServiceClient(account_url=account_url,credential=setcredentials_name_key.key)
        elif isinstance(set_credentials,SetCredentialsConnectionString):
            set_credentials_connection_string:SetCredentialsConnectionString=set_credentials
            self.__connection_string=set_credentials_connection_string.connection_string
            pattern='DefaultEndpointsProtocol=(.*?);AccountName=(.*?);AccountKey=(.*?);EndpointSuffix=(.*)'
            DefaultEndpointsProtocol, AccountName, AccountKey, EndpointSuffix = re.match(pattern, self.__connection_string).groups()
            self.__account_name=AccountName
            self.__account_key=AccountKey
            self.__account_url=account_url_template.format(AccountName)
            self.__service_client_conn = BlobServiceClient.from_connection_string(conn_str=set_credentials_connection_string.connection_string)
        else:
            self.__service_client_conn = None

    #############################################
    # Connect/Info Zone

    def get_connect_status(self):
        '''Description

        :return bool: True if exist attribute sku_name in account_information, otherwise return False due to connection failure to the storage account

        ## Examples

        ```Python
        from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsNameKey, SetCredentialsConnectionString

        asabm=AzureStorageAccountBlobManagement(SetCredentialsNameKey(account_name="",key=""))
        print("SetCredentialsNameKey: Successfully connection") if asabm.get_connect_status() else print("SetCredentialsNameKey: Failed connection")

        asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=""))
        print("SetCredentialsNameKey: Successfully connection") if asabm.get_connect_status() else print("SetCredentialsNameKey: Failed connection")

        ```
        '''
        try:
            self.__service_client_conn.get_account_information()
            return True
        except Exception as e:
            return False

    def get_account_information(self):
        '''Description

        :return list: list of account information

        ## Examples

        ```Python
        from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString
        import json

        asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=""))
        data=asabm.get_account_information()
        print(json.dumps(data,indent=4))
        ```
        '''
        return json.loads(json.dumps(self.__service_client_conn.get_account_information(), sort_keys=True, default=str))

    #############################################
    # Container Zone

    def container_list(self):
        '''Description

        :return list: A list of full data of containers according to the given credentials
        '''
        list_containers=[]
        try:
            containers = self.__service_client_conn.list_containers()
            for container in containers:
                list_containers.append(container)
        except Exception as e:
            return list_containers
        return list_containers

    def container_list_name(self):
        '''Description

        :return list: A list names of containers according to the given credentials
        '''
        list_containers=[]
        try:
            containers = self.__service_client_conn.list_containers()
            for container in containers:
                list_containers.append(container.name)
        except Exception as e:
            return list_containers
        return list_containers

    def container_create(self,name:str,
                public_access:Literal[
                    PublicAccess.BLOB,
                    PublicAccess.CONTAINER,
                    PublicAccess.OFF,
                ] | None = None,
                ignore_if_exists: bool = True
            )->bool|str:
        '''Description

        :param name:str         : Name of new container.
        :param public_access:str: Possible values None,container,blob. Default value None for private access.
        :return bool|str        : True if Ok, otherwise string message exception.

        ## Example
        ```Python
        from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString

        asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=""))

        status=asabm.container_create("name")
        # status=asabm.container_create("name","blob") # for public access
        if status is True:
            print("ok...")
        else:
            print(status)
        ```
        '''
        status=True
        try:
            name=str(name)
            if isinstance(public_access,str): public_access = public_access.lower()
            allowed_values = [str(pa.value) for pa in PublicAccess]+[None]
            if public_access not in allowed_values:
                return f"Not allowed value, allowed values ​​are: {allowed_values}"
            self.__service_client_conn.create_container(name=name,public_access=public_access)
        except HttpResponseError as ex:
            error_code = getattr(ex, "error_code", None)
            match error_code:
                case "PublicAccessNotPermitted":
                    return f"The container {name} could not be created. Public access to this storage account is not allowed."
                case "ContainerAlreadyExists":
                    if ignore_if_exists:
                        return True
                    else:
                        return f"The specified container {name} already exists."
        except Exception as e:
            status=str(e)
        return status

    def container_delete(self,name:str)->bool|str:
        '''Description

        :param name:str     : Name of new container.
        :return bool|str    : True if Ok, otherwise string message exception.

        ## Example
        ```Python
        from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString

        asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=""))
        status=asabm.container_delete("name")
        if status is True:
            print("ok...")
        else:
            print(status)
        ```
        '''
        status=True
        try:
            self.__service_client_conn.delete_container(str(name))
        except ResourceNotFoundError as ex:
            status=str(ex)
        except Exception as e:
            status=str(e)
        return status

    #############################################
    # BlockBlob Zone

    def container_blob_list(self,container_name:str,container_folders:list[str]=[],include_subfolders:bool=True,modified_minutes_ago:int=None)->list[BlobProperties]:
        '''Description

        Lists the files in a container and its subfolders, returning their properties.
        :param container_name:str       : Name of container.
        :param include_subfolders:bool  : Return results from subfolders or only in the defined folder. 
        :param modified_minutes_ago:int : If it is not null but a number, files modified more than x minutes ago will be returned.
        :return list                    : list of blobs in container name.

        ## Example
        ```Python
        from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString
        from azure.storage.blob import BlobProperties

        asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=""))
        blob_list=asabm.container_blob_list("container_name")
        if(isinstance(blob_list,list)):
            for blob in blob_list:
                print("----------------------")
                blob_properties:BlobProperties = blob
                print(f"name: {blob_properties.name}")
                print(f"size: {blob_properties.size} bytes")
                print(f"content_md5: {blob_properties.content_settings.content_md5}")
                print(f"last_modified: {blob_properties.last_modified}")
                print(f"blob_type: {blob_properties.blob_type}")        
        else:
            print(blob_list)
        ```
        '''
        try:            
            container_name=str(container_name)
            container_client = self.__service_client_conn.get_container_client(container_name)
            if len(container_folders)==0:
                blob_list = [blob for blob in container_client.walk_blobs(delimiter='/')]
                container_client.dep                
            else:
                path_blob = "/".join(container_folders)
                blob_list = [blob for blob in container_client.list_blobs(name_starts_with=path_blob)]
            if include_subfolders is True and modified_minutes_ago is None:
                return blob_list
            else:
                now = datetime.datetime.now(timezone.utc)
                blob_filter_list=[]
                for blob in blob_list:
                    if isinstance(blob, BlobPrefix):
                        print(blob.name)
                for blob in blob_list:
                    analyze_item=True
                    if include_subfolders is False:
                        subfolders_len=len(blob.name.split("/"))-1
                        if len(container_folders) != subfolders_len:
                            analyze_item=False                    
                    if analyze_item is True:
                        if modified_minutes_ago is None:
                            blob_filter_list.append(blob)
                        else:
                            time_diff = now - blob.last_modified
                            if time_diff > timedelta(minutes=modified_minutes_ago):
                                blob_filter_list.append(blob)
                return blob_filter_list            
        except ResourceNotFoundError as ex:
            return str(ex)
        except Exception as e:
            return str(e)

    def container_blob_properties(self,blob_file:str,container_name:str,container_folders:list[str]=[])->BlobProperties|str:
        '''Description

        :param blob_file:str                : Blob name with extention to get the info.
        :param container_name:str           : Name of container.
        :param container_folders:list[str]  : Subfolders where the blob file is located. Default root container.
        :return list                        : BlobProperties or Exception message

        ## Example
        ```Python
        from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString
        from azure.storage.blob import BlobProperties

        asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=""))

        # Example 1 - Small file
        # Container root path
        blob_file='upload.txt'
        blob_properties:BlobProperties=asabm.container_blob_properties(blob_file,"container_name")
        if isinstance(blob_properties,BlobProperties):
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
        blob_properties:BlobProperties=asabm.container_blob_properties(blob_file,"container_name",container_folders)
        if isinstance(blob_properties,BlobProperties):
            print(f"name: {blob_properties.name}")
            print(f"size: {blob_properties.size} bytes")
            print(f"content_md5: {blob_properties.content_settings.content_md5}")
            print(f"last_modified: {blob_properties.last_modified}")
            print(f"blob_type: {blob_properties.blob_type}")        
        else:
            print(blob_properties)

        ```
        '''
        try:
            path_blob = "/".join(container_folders + [blob_file])
            container_name=str(container_name)
            container_client = self.__service_client_conn.get_container_client(container_name)
            blob_client = container_client.get_blob_client(path_blob)
            if blob_client.exists():
                blob_properties:BlobProperties = blob_client.get_blob_properties()
                return blob_properties
            else:
                return AzureStorageAccountBlobManagementErrorCode.BLOB_FILE_NOT_FOUND
        except Exception as e:
            return str(e)

    def container_blob_upload_staging_blocks_commit(self,folder_local_full_path:str,file_to_upload:str,container_name:str,container_folders:list[str]=[],verify_file_integrity:bool=False,print_charge_percentage:bool=False)->bool|str:
        '''Description

        upload the file using block preparation and commit, and use the md5 checksum of the file content to verify the integrity of the uploaded blob content.
        This function allows you to limit the ram memory used by reading in chunks but not the network connections to be used to improve the upload speed.
        It can show the status progress.
        Formats that failed (InvalidBlobOrBlock): mp4, backup
        
        :param folder_local_full_path:str   : Name of container.
        :param file_to_upload:str           : File name with extention to upload.
        :param container_name:str           : Container name.
        :param container_folders:list[str]  : Subfolders to upload files to the container. Default root container.
        :param verify_file_integrity:bool   : Enable checksum verification with content_md5
        :param print_charge_percentage:bool : prints data and percentage of progress of the process in the console.
        :return bool|str                    : True if Ok, otherwise string message exception.

        ## Examples

        ```Python
        from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString
        from jaanca_chronometer import Chronometer # pip install jaanca-chronometer
        import os

        asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=""))
        chronometer=Chronometer()
        folder_local_full_path=os.path.abspath(os.path.join(os.path.dirname(__file__),'files'))
        file='upload.txt'

        # Container root path
        chronometer.start()
        status=asabm.container_blob_upload_staging_blocks_commit(folder_local_full_path,file,"container",verify_file_integrity=True,print_charge_percentage=True)
        chronometer.stop()
        if status is True:
            print("blob:[{}] uploaded...".format(os.path.join(folder_local_full_path,file)))
            print(f"Elapsed time: {chronometer.get_elapsed_time()}")
        else:
            print(status)

        # Container and subfolders path
        container_folders=["folder1","folder2"]
        chronometer.start()
        status=asabm.container_blob_upload_staging_blocks_commit(folder_local_full_path,file,"container",container_folders,verify_file_integrity=True,print_charge_percentage=True)
        chronometer.stop()
        if status is True:
            print("folders container_name:{}, blob:[{}] uploaded...".format(container_folders,os.path.join(folder_local_full_path,file)))
            print(f"Elapsed time: {chronometer.get_elapsed_time()}")
        else:
            print(status)
        ```

        # References

        https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-upload-python


        '''
        try:
            container_name=str(container_name)
            path_blob = "/".join(container_folders + [file_to_upload])
            path_file=os.path.join(folder_local_full_path,file_to_upload)
            container_client = self.__service_client_conn.get_container_client(container_name)
            blob_client = container_client.get_blob_client(path_blob)
            if print_charge_percentage is True:
                total_file_size_bytes = os.path.getsize(path_file)
                total_chunks = math.ceil(total_file_size_bytes / self.__chunk_size_bytes)
                uploaded_chunks = 0
            if blob_client.exists():
                blob_client.delete_blob()
            status=self.checksum_get_local_content_md5(path_file,is_string=False)
            if status is False:
                return status
            content_settings=ContentSettings(content_md5=status)
            with open(file=path_file, mode="rb") as file_stream:
                block_id_list = []
                while True:
                    buffer = file_stream.read(self.__chunk_size_bytes)
                    if not buffer:
                        break
                    block_id = uuid.uuid4().hex
                    block_id_list.append(BlobBlock(block_id=block_id))
                    blob_client.stage_block(block_id=block_id, data=buffer, length=len(buffer))
                    if print_charge_percentage is True:
                        uploaded_chunks+=1
                        upload_percentage = (uploaded_chunks / total_chunks) * 100
                        print(f"Upload process: file_to_upload[{file_to_upload}], Chunks[{uploaded_chunks}/{total_chunks}], Percentage[{upload_percentage:.2f}%]")
                blob_client.commit_block_list(block_id_list,content_settings=content_settings)
            if verify_file_integrity is True:
                verify_file_integrity = self.checksum_compare_local_file_versus_remote_content_md5(folder_local_full_path,file_to_upload,container_name,container_folders)
                if verify_file_integrity is True:
                    return True
                else:
                    return verify_file_integrity
            else:
                return True
        except Exception as e:
            return str(e)

    def container_blob_upload_data_transfer_options(self,folder_local_full_path:str,file_to_upload:str,container_name:str,container_folders:list[str]=[],max_concurrency:int=2,verify_file_integrity:bool=False)->bool|str:
        '''Description

        Upload file using multiple network upload connections, and use the md5 checksum of the file content to verify the integrity of the uploaded blob content..
        This function allows you to limit the ram memory used by reading in chunks and the network connections to be used to improve the upload speed.
        
        :param folder_local_full_path:str   : Name of container.
        :param file_to_upload:str           : File name with extention to upload.
        :param container_name:str           : Container name.
        :param container_folders:list[str]  : Subfolders to upload files to the container. Default root container.
        :param max_concurrency:int          : This argument defines the maximum number of parallel connections to use when the blob size exceeds 64 MiB.
        :param verify_file_integrity:bool   : Enable checksum verification with content_md5
        :return bool|str                    : True if Ok, otherwise string message exception.

        ## Examples

        ```Python
        from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString
        from jaanca_chronometer import Chronometer # pip install jaanca-chronometer
        import os
        
        chronometer=Chronometer()
        asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=""))

        # Container root path
        folder_local_full_path=os.path.abspath(os.path.join(os.path.dirname(__file__),'files'))
        file='upload.txt'
        chronometer.start()
        status=asabm.container_blob_upload_data_transfer_options(folder_local_full_path,file,"container",max_concurrency=,verify_file_integrity=True)
        chronometer.stop()
        if status is True:
            print("blob:[{}] uploaded...".format(os.path.join(folder_local_full_path,file)))
            print(f"Elapsed time: {chronometer.get_elapsed_time()}")
        else:
            print(status)

        # Container and subfolders path
        container_folders=["folder1","folder2"]
        folder_local_full_path=os.path.abspath(os.path.join(os.path.dirname(__file__),'files'))
        file='upload.txt'
        chronometer.start()
        status=asabm.container_blob_upload_data_transfer_options(folder_local_full_path,file,"container"A,container_folders,max_concurrency=2,verify_file_integrity=True)
        chronometer.stop()
        if status is True:
            print("blob:[{}] uploaded...".format(os.path.join(folder_local_full_path,file)))
            print(f"Elapsed time: {chronometer.get_elapsed_time()}")
        else:
            print(status)
        ```

        # References

        https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-upload-python


        '''
        try:
            container_name=str(container_name)
            path_blob = "/".join(container_folders + [file_to_upload])
            path_file=os.path.join(folder_local_full_path,file_to_upload)
            blob_client = BlobClient(
                account_url=self.__account_url, 
                container_name=container_name,
                blob_name=path_blob,
                credential=self.__account_key,
                max_block_size=self.__chunk_size_bytes,
                max_single_put_size=self.__max_single_put_size
            )

            status=self.checksum_get_local_content_md5(path_file,is_string=False)
            if status is False:
                return status

            content_settings=ContentSettings(content_md5=status)
            with open(file=path_file, mode="rb") as data:
                blob_client = blob_client.upload_blob(data=data, overwrite=True, max_concurrency=max_concurrency,content_settings=content_settings)

            if verify_file_integrity is True:
                verify_file_integrity = self.checksum_compare_local_file_versus_remote_content_md5(folder_local_full_path,file_to_upload,container_name,container_folders)
                if verify_file_integrity is True:
                    return True
                else:
                    return verify_file_integrity
            else:
                return True
        except Exception as e:
            return str(e)

    def container_blob_download_data_transfer_options(self,folder_local_full_path:str,file_to_download:str,container_name:str,container_folders:list[str]=[],max_concurrency:int=2,verify_file_integrity:bool=False,file_new_name:str|None = None)->bool|str:
        '''Description

        You can set configuration options when instantiating a client to optimize performance for data transfer operations.
        This function use the md5 checksum of the file content to verify the integrity of the downloaded blob content.
        
        :param folder_local_full_path:str   : Name of container.
        :param file_to_download:str         : File name with extention to download.
        :param container_name:str           : Container name.
        :param container_folders:list[str]  : Subfolders to upload files to the container. Default root container.
        :param max_concurrency:int          : This argument defines the maximum number of parallel connections to use when the blob size exceeds 64 MiB.
        :param verify_file_integrity:bool   : Enable checksum verification with content_md5
        :param file_new_name:str|None       : Rename the file before downloading it
        :return bool|str                    : True if Ok, otherwise string message exception.

        ## Examples

        ```Python
        from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString
        from jaanca_chronometer import Chronometer # pip install jaanca-chronometer
        import os

        asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=""))
        chronometer=Chronometer()

        # Container root path
        folder_local_full_path=os.path.abspath(os.path.join(os.path.dirname(__file__),'files_download'))
        file='upload.txt'
        chronometer.start()
        status=asabm.container_blob_download_data_transfer_options(folder_local_full_path,file,"container",max_concurrency=2,verify_file_integrity=True)
        chronometer.stop()
        if status is True:
            print("blob:[{}] downloaded...".format(os.path.join(folder_local_full_path,file)))
            print(f"Elapsed time: {chronometer.get_elapsed_time()}")
        else:
            print(status)

        # Container and subfolders path
        folder_local_full_path=os.path.abspath(os.path.join(os.path.dirname(__file__),'files_download'))
        container_folders=["folder1","folder2"]
        file='upload.txt'
        chronometer.start()
        status=asabm.container_blob_download_data_transfer_options(folder_local_full_path,file,"container",container_folders,max_concurrency=2,verify_file_integrity=True)
        chronometer.stop()
        if status is True:
            print("blob:[{}] downloaded...".format(os.path.join(folder_local_full_path,file)))
            print(f"Elapsed time: {chronometer.get_elapsed_time()}")
        else:
            print(status)
        ```

        # References

        https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-download-python
        
        https://learn.microsoft.com/en-us/python/api/overview/azure/storage-blob-readme?view=azure-python#downloading-a-blob
        Retry Policy configuration
            Use the following keyword arguments when instantiating a client to configure the retry policy:
                retry_total (int): Total number of retries to allow. Takes precedence over other counts. Pass in retry_total=0 if you do not want to retry on requests. Defaults to 10.
                retry_connect (int): How many connection-related errors to retry on. Defaults to 3.
                retry_read (int): How many times to retry on read errors. Defaults to 3.
                retry_status (int): How many times to retry on bad status codes. Defaults to 3.
                retry_to_secondary (bool): Whether the request should be retried to secondary, if able. This should only be enabled of RA-GRS accounts are used and potentially stale data can be handled. Defaults to False.

        '''
        try:
            container_name=str(container_name)
            path_blob = "/".join(container_folders + [file_to_download])
            if file_new_name is None:
                path_file=os.path.join(folder_local_full_path,file_to_download)
            else:
                path_file=os.path.join(folder_local_full_path,file_new_name)
            blob_client = BlobClient(
                account_url=self.__account_url, 
                container_name=container_name,
                blob_name=path_blob,
                credential=self.__account_key,
                max_block_size=self.__chunk_size_bytes
            )
            
            with open(file=path_file, mode="wb") as data:
                download_stream = blob_client.download_blob(max_concurrency=max_concurrency)
                download_stream.readinto(data)

            verify_file_integrity = self.checksum_compare_local_file_versus_remote_content_md5(folder_local_full_path,file_to_download,container_name,container_folders,file_new_name=file_new_name)
            if verify_file_integrity is True:
                return True
            else:
                return verify_file_integrity
        except Exception as e:
            return str(e)

    def container_blob_delete(self,file_to_delete:str,container_name:str,container_folders:list[str]=[])->bool|str:
        '''Description

        :param file_to_delete:str           : File name with extention to delete.
        :param container_name:str           : Container name.
        :param container_folders:list[str]  : Subfolders to upload files to the container. Default root container.
        :return bool|str                    : True if Ok, otherwise string message exception.

        ## Examples

        ```Python
        from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString
        import os

        asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=""))

        # Container root path
        file='upload.txt'
        status=asabm.container_blob_delete(file,App.AzureStorageAccount.Containers.NAME_WITH_DATA)
        if status is True:
            print("blob:[{}] deleted...".format(os.path.join(file)))
        else:
            print(status)

        # Subfolders
        container_folders=["folder1","folder2"]
        file='upload.txt'
        status=asabm.container_blob_delete(file,App.AzureStorageAccount.Containers.NAME_WITH_DATA,container_folders=container_folders)
        if status is True:
            path_blob = "/".join(container_folders + [file])
            print("blob:[{}] deleted...".format(path_blob))
        else:
            print(status)

        ```

        # References

        https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-download-python


        '''
        try:
            container_name=str(container_name)
            path_blob = "/".join(container_folders + [file_to_delete])
            container_client = self.__service_client_conn.get_container_client(container_name)
            blob_client = container_client.get_blob_client(path_blob)            
            if blob_client.exists():
                blob_client.delete_blob()
            return True
        except Exception as e:
            return str(e)

    def container_blob_get_url_sas_read_to_download(self,file_to_download:str,container_name:str,container_folders:list[str]=[],expiry_days:int=1)->bool|str:
        '''Description

        You can set configuration options when instantiating a client to optimize performance for data transfer operations.
        
        :param file_to_download:str         : File name with extention to download.
        :param container_name:str           : Container name.
        :param container_folders:list[str]  : Subfolders to upload files to the container. Default root container.
        :param expiry_days:int              : days duration for the sas token.
        :return bool|str                    : False if there is an error or the blob file does not exist, otherwise sas url to download file.

        ## Examples

        ```Python
        import os
        ```

        # References

        https://learn.microsoft.com/en-us/azure/storage/blobs/sas-service-create-python


        '''
        try:
            container_name=str(container_name)
            path_blob = "/".join(container_folders + [file_to_download])
            container_client = self.__service_client_conn.get_container_client(container_name)
            blob_client = container_client.get_blob_client(path_blob)            
            if blob_client.exists():
                start_time = datetime.datetime.now(datetime.timezone.utc)
                expiry_time = start_time + datetime.timedelta(days=expiry_days)
                sas_token = generate_blob_sas(
                    account_name=self.__account_name,
                    container_name=container_name,
                    blob_name=path_blob,
                    account_key=self.__account_key,
                    permission=BlobSasPermissions(read=True, write=False, delete=False, list=False, add=False),
                    expiry=expiry_time,
                    start=start_time
                )
                url=self.__account_url+"/"+container_name+"/"+path_blob+"?"+sas_token
                return url
            else:
                return False
        except Exception as e:
            return False

    def container_blob_upload_logging(self,container_name:str,logging_level:LoggingLevels,preffix_name:str,message:str,prefix_within_the_message:str='',container_folders:list[str]=[])->bool|str:
        '''Description

        Use this method to write messages to the end of a blob file.
        :param container_name:str               : Container name.
        :param logging_level:LoggingLevels      : Suffix for name: logging_level to name the file, example for info would be: "info.log".
        :param preffix_name:str                 : Prefix for name: it will be the beginning of the file name, example: "application.info.log".
        :param message:str                      : Message to write to the file.
        :param prefix_within_the_message:str    : Text to write to the file before the message, to differentiate messages. Suggested date and time.
        :param container_folders:list[str]      : Subfolders to upload files to the container. Default logs folder at the root of the container.
        :return bool|str                        : True if Ok, otherwise string message exception.

        ## Examples

        ```Python
        from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString

        asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=""))

        # Example 1 - INFO
        # Container root path
        preffix_name="app_worker"
        message = "text text...\ntext text...\ntext text...\ntext text...\n"
        status=asabm.container_blob_upload_logging("container",LoggingLevels.INFO,"aplication_name","message","2024-05-10 12:25:25")
        if status is True:
            print("blob file message: uploaded...")
        else:
            print(status)

        # Example 1 - ERROR
        # Container and subfolders path
        preffix_name="app_worker"
        container_folders=["fastapi","logs"]
        message = """text text...
        text text...
        text text...
        text text...
        """
        status=asabm.container_blob_upload_logging("container",LoggingLevels.INFO,"aplication_name","message","2024-05-10 12:25:25",container_folders)
        if status is True:
            print("blob file message: uploaded...")
        else:
            print(status)        
        
        ```
        '''
        try:
            container_name=str(container_name)
            preffix_name=preffix_name.replace(" ","")
            file_to_upload=f"{preffix_name}.{LoggingLevels(logging_level)}.log"
            if prefix_within_the_message == '':
                message=str(message)
            else:
                message=f"{prefix_within_the_message} {message}"
            path_blob = "/".join(container_folders + [file_to_upload])
            container_client = self.__service_client_conn.get_container_client(container_name)
            blob_client = container_client.get_blob_client(path_blob)            
            if not blob_client.exists():
                blob_client.create_append_blob()                
            data = message.encode()
            blob_client.append_block(data, length=len(data))
            return True
        except Exception as e:
            return str(e)

    def container_blob_read_logging_latest_changes(self,container_name:str,file_log:str,container_folders:list[str]=[],seconds_refresh:int=3)->bool|str:
        '''Description

        Execute this method in the console or terminal, the content of the file will begin to print until the last line, where changes are monitored.
        It works similar to how it works in the linux tail -1 console, where the latest changes to the file are printed.

        :param container_name:str           : Container name.
        :param file_log:str                 : File to read for latest changes.
        :param container_folders:list[str]  : Subfolders to upload files to the container. Default logs folder at the root of the container.
        :param seconds_refresh:int          : Text to write to the file before the message, to differentiate messages. Suggested date and time.
        :return bool|str                    : True if Ok, otherwise string message exception.

        ## Examples

        ```Python

        
        ```
        '''
        try:
            container_name=str(container_name)
            path_blob = "/".join(container_folders + [file_log])
            container_client = self.__service_client_conn.get_container_client(container_name)
            blob_client = container_client.get_blob_client(path_blob)            
            if not blob_client.exists():
                return False

            def read_latest_changes():
                current_length = blob_client.get_blob_properties().size
                if current_length > read_latest_changes.previous_length:
                    new_data = blob_client.download_blob(offset=read_latest_changes.previous_length)
                    new_content = new_data.readall().decode('utf-8')
                    print(new_content)
                    read_latest_changes.previous_length = current_length

            read_latest_changes.previous_length = 0
            while True:
                read_latest_changes()
                time.sleep(seconds_refresh)

        except Exception as e:
            return str(e)

    def checksum_get_local_content_md5(self,full_path_file:str,is_string:bool=True)->bool|str|bytearray:
        '''Description

        :full_path_file:str         : Full disk path to file.
        :is_string:bool             : If True hexadecimal representation of the file checksum, if False bytearray.
        :return bool|str|bytearray  : False if there is an error, otherwise checksum of file.
        '''
        try:
            with open(full_path_file, "rb") as data:
                local_content_md5 = hashlib.md5()
                for chunk in iter(lambda: data.read(self.__chunk_size_bytes), b""):
                    local_content_md5.update(chunk)
            local_content_md5=local_content_md5.hexdigest()
            if is_string is True:
                return local_content_md5
            else:
                return bytearray.fromhex(local_content_md5)
        except Exception as e:
            return False

    def checksum_compare_local_file_versus_remote_content_md5(self,folder_local_full_path:str,file:str,container_name:str,container_folders:list[str]=[],file_new_name:str|None = None)->bool|str|bytearray:
        '''Description

        Compare checksum md5 hash of a local file against the cotent_md5 blob properties.
        Compares the local size of the file and the blob, ensuring that if locally it is greater than 0 bytes, the remote one is also greater than 0 bytes.
        
        :param folder_local_full_path:str   : Name of container.
        :param file:str                     : File name with extention to compare.
        :param container_name:str           : Container name.
        :param container_folders:list[str]  : Subfolders to upload files to the container. Default root container.
        :param file_new_name:str|None       : This is the new name of file, if the file has been renamed.
        :return bool|str                    : True if Ok, otherwise string message exception.

        ## Example
        
        ```Python
        from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString
        import os

        asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=""))
        folder_local_full_path=os.path.abspath(os.path.join(os.path.dirname(__file__),'files'))

        # Example 1 - Small file
        # Container root path
        file='upload.txt'
        status=asabm.checksum_compare_local_file_versus_remote_content_md5(folder_local_full_path,file,"Container")
        if status is True:
            print("blob:[{}]  checksum ok...".format(os.path.join(folder_local_full_path,file)))
        else:
            print(status)

        # Example 2 - Small file
        # Container and subfolders path
        file='upload.txt'
        container_folders=["folder1","folder2"]
        status=asabm.checksum_compare_local_file_versus_remote_content_md5(folder_local_full_path,file,"Container",container_folders)
        if status is True:
            print("blob:[{}]  checksum ok...".format(os.path.join(folder_local_full_path,file)))
        else:
            print(status)        

        '''
        try:
            container_name=str(container_name)
            path_blob = "/".join(container_folders + [file])            

            if file_new_name is None:
                path_file=os.path.join(folder_local_full_path,file)
            else:
                path_file=os.path.join(folder_local_full_path,file_new_name)

            local_content_md5=self.checksum_get_local_content_md5(path_file)
            container_client = self.__service_client_conn.get_container_client(container_name)
            blob_client = container_client.get_blob_client(path_blob)
            blob_properties = blob_client.get_blob_properties()
            remote_content_md5 = blob_properties.content_settings.content_md5
            if remote_content_md5 is None:
                return AzureStorageAccountBlobManagementErrorCode.CHECKSUM_CONTENT_MD5_NOT_FOUND
            else:
                remote_content_md5 = remote_content_md5.hex()
                if local_content_md5 == remote_content_md5:
                    data:BlobProperties=self.container_blob_properties(file,container_name,container_folders)
                    if isinstance(blob_properties,BlobProperties):
                        remote_size = data.size
                        local_size = os.path.getsize(path_file)
                        if(local_size == remote_size):
                            return True
                        else:
                            return AzureStorageAccountBlobManagementErrorCode.LOCAL_AND_REMOTE_SIZE_DO_NOT_MATCH
                    else:
                        return blob_properties
                else:
                    return AzureStorageAccountBlobManagementErrorCode.CHECKSUM_CONTENT_MD5_VERSUS_NOT_MATCH
        except Exception as e:
            return str(e)