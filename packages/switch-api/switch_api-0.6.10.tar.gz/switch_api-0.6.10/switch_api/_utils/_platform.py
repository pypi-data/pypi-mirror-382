# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for .....
"""
from io import StringIO
import os
from azure.storage.blob import ContainerClient, BlobClient, ContentSettings
import uuid
import pandas
import time
import requests
import logging
import sys
import random

from azure.core.exceptions import AzureError, ResourceNotFoundError
from .._utils._constants import ACCOUNT, DATA_INGESTION_CONTAINER
from .._utils._utils import ApiInputs


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  switch_api.%(module)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)


class Queue:
    """ """
    @staticmethod
    def get_next_messages(account: ACCOUNT, container: str, queue_name: str, message_count: int = 1):
        """Retrieve next message(s).

        Parameters
        ----------
        account : ACCOUNT
            Azure account
        container : str
            Queue container.
        queue_name : str
            Queue name.
        message_count : int
            Message count to retrieve (Default value = 1).

        Returns
        -------

        """
        pass

    @staticmethod
    def send_message(account: ACCOUNT, container, queue_name, messages: list = None):
        """Send message

        Parameters
        ----------
        account : ACCOUNT
            Azure account.
        container : str
            Queue container.
        queue_name : str
            Queue name.
        messages : list, default = None
            Message (Default value = None).

        Returns
        -------

        """
        if messages is None:
            messages = []

        pass


class Blob:
    """ """
    @staticmethod
    def list(api_inputs: ApiInputs, account: ACCOUNT, container: str, prefix: str = None):
        """Retrieve list of blobs.

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by initialize() function.
        account : ACCOUNT
            Azure account.
        container : str
            Blob container.
        prefix : str, default=None
            Prefix (Default value = None).

        Returns
        -------

        """

        if not set([account]).issubset(set(ACCOUNT.__args__)):
            logger.error('account parameter must be set to one of the allowed values defined by the '
                         'ACCOUNT literal: %s', ACCOUNT.__args__)
            return False

        if prefix is None:
            prefix = ''

        container_con_string = _get_container_sas_uri(api_inputs, container, account)
        container_client = ContainerClient.from_container_url(container_con_string)

        blob_list = container_client.list_blobs(name_starts_with=prefix)
        for blob in blob_list:
            logger.info('%s - %s', blob.name, str(blob.last_modified))
        return True

    @staticmethod
    def download(api_inputs: ApiInputs, account: ACCOUNT, container: str, blob_name: str):
        """

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by initialize() function.
        account : ACCOUNT
            Azure account
        container : str
            Blob container.
        blob_name : str
            Blob name.

        Returns
        -------

        """
        if not set([account]).issubset(set(ACCOUNT.__args__)):
            logger.error('account parameter must be set to one of the allowed values defined by the '
                         'ACCOUNT literal: %s', ACCOUNT.__args__)
            return False

        container_con_string = _get_container_sas_uri(api_inputs, container, account)
        container_client = ContainerClient.from_container_url(container_con_string)

        blob_client = container_client.get_blob_client(blob_name)

        return blob_client.download_blob().readall()

    @staticmethod
    def upload(api_inputs: ApiInputs, data_frame: pandas.DataFrame, name: str, batch_id: uuid.UUID = None, account: ACCOUNT = 'DataIngestion',
               container: DATA_INGESTION_CONTAINER = 'data-ingestion-adx', folder: str = 'to-ingest', include_header: bool = False):
        """Upload data to blob.

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by initialize() function.
        account: ACCOUNT, optional
            Blob account data will be uploaded to (Default value = 'DataIngestion').
        data_frame : pandas.DataFrame
            Dataframe containing the data to be uploaded to blob.
        name : str
            Name.
        batch_id : str
            Data feed file status id.
        folder: str
            Top folder inside the container assigned to the uploaded blob. (Default value = 'to-ingest')
        container: DATA_INGESTION_CONTAINER
            Container name (Literal) to where the blob goes into. (Default value = 'data-ingestion-adx')
        include_header: bool
            Boolean if include data frame's headers in the output file.
            Default to False

        Returns
        -------

        """
        csv_df = data_frame.copy()
        
        # Get size in bytes
        def get_csv_size(df):
            buffer = StringIO()
            df.to_csv(buffer, index=False)
            size_in_bytes = buffer.tell()  
            buffer.close()
            return size_in_bytes

        # Splitting DataFrame into chunks
        def split_dataframe(df, chunk_size):
            for i in range(0, len(df), chunk_size):
                yield df.iloc[i:i + chunk_size]
                
        def format_size(bytes_size):
            # Define size units in increasing order
            units = ['B', 'KB', 'MB', 'GB', 'TB']
            size = bytes_size
            unit_index = 0

            # Divide size until it's smaller than 1024 or we run out of units
            while size >= 1024 and unit_index < len(units) - 1:
                size /= 1024
                unit_index += 1

            return f"{size:.2f} {units[unit_index]}"

                
        # 3 MB in bytes
        max_size = 3 * 1024 * 1024  

        if not set([account]).issubset(set(ACCOUNT.__args__)):
            logger.error('account parameter must be set to one of the allowed values defined by the '
                         'ACCOUNT literal: %s', ACCOUNT.__args__)
            return False

        if not set([container]).issubset(set(DATA_INGESTION_CONTAINER.__args__)):
            logger.error('container parameter must be set to one of the allowed values defined by the '
                         'DATA_INGESTION_CONTAINER literal: %s', DATA_INGESTION_CONTAINER.__args__)
            return False

        if batch_id is None or batch_id == '00000000-0000-0000-0000-000000000000' or batch_id == '':
            if api_inputs.data_feed_file_status_id is None \
                    or api_inputs.data_feed_file_status_id == '00000000-0000-0000-0000-000000000000':
                batch_id = uuid.uuid4()
            else:
                batch_id = api_inputs.data_feed_file_status_id

        container_con_string = _get_container_sas_uri(api_inputs, container, account, True)
        container_client = ContainerClient.from_container_url(container_con_string)

        csv_size = get_csv_size(csv_df)
        logger.info(f"Total Dataframe File Size: {format_size(csv_size)}")
        rows_per_partition = max_size // (csv_size / len(csv_df))
        chunk_size = int(rows_per_partition)

        upload_path = f"{folder}/{api_inputs.api_project_id}/{name}/{batch_id}/{time.time_ns()}_"

        item_counter = 0
        for i, current_data_frame in enumerate(split_dataframe(csv_df, chunk_size)):
            item_counter += 1
            blob_name = upload_path + str(item_counter) + ".csv"
            logger.info("Uploading ... %s, file size=%s",
                        blob_name, format_size(get_csv_size(current_data_frame)))
            blob_client = container_client.get_blob_client(blob_name)

            if pandas.__version__ < "1.5.0":
                data_csv = bytes(current_data_frame.to_csv(line_terminator='\r\n', index=False, header=include_header),
                                 encoding='utf-8')
            elif pandas.__version__ >= "1.5.0":
                data_csv = bytes(current_data_frame.to_csv(lineterminator='\r\n', index=False, header=include_header),
                                 encoding='utf-8')
            blob_client.upload_blob(
                data_csv, blob_type="BlockBlob", overwrite=True)


        return upload_path, item_counter

    @staticmethod
    def custom_upload(api_inputs: ApiInputs, account: ACCOUNT, container: str, upload_path: str, file_name: str,
                      upload_object):
        """Upload data to blob.

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by initialize() function.
        account: ACCOUNT
            Blob account data will be uploaded to.
        container : str
            Blob container.
        upload_path: str
            The prefix required to navigate from the base `container` to the folder the `upload_object` should be
            uploaded to.
        file_name : str
            File name to be stored in blob.
        upload_object :
            Object to be uploaded to blob.

        Returns
        -------

        """
        if not set([account]).issubset(set(ACCOUNT.__args__)):
            logger.error('account parameter must be set to one of the allowed values defined by the '
                         'ACCOUNT literal: %s', ACCOUNT.__args__)
            return False

        container_con_string = _get_container_sas_uri(api_inputs, container, account, True)
        container_client = ContainerClient.from_container_url(container_con_string)

        if upload_path.endswith('/') == False:
            blob_name = upload_path + '/' + file_name
        elif upload_path.endswith('/') == True:
            blob_name = upload_path + file_name

        logger.info('Uploading to blob: %s', blob_name)
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(upload_object, blob_type="BlockBlob", overwrite=True)

    @staticmethod
    def _rename(api_inputs: ApiInputs, old_blob_name: str, new_blob_name: str, timeout: int = 60):
        """
        Renames a blob by copying it to a new name (path) and deleting the old one.
        Restricted to work on 'DataIngestion` Storage Account and `assets` Container.

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by initialize() function.
        old_blob_name : str
            Name of the existing blob to be renamed.
        new_blob_name : str
            New name for the blob (must not already exist).
        timeout : int, optional
            Maximum number of seconds to wait for the rename (copy) operation to complete
            before aborting. 
            Default is 60 seconds (1 minute). Capped at 300 seconds (5 minutes).

        Returns
        -------
        dict
            Dictionary containing the result of the rename operation with keys:
            - old_blob (str): The original blob name.
            - new_blob (str): The new blob name.
            - copy_status (str): "success", "failed", "aborted", or "timeout".
            - delete_status (str or None): "success" or "failed" (None if copy failed).
            - message (str): Summary of the operation result.
        """
        
        # Safeguards: restrict Account Storage to "Data Ingestion" and restrict Container to "assets"
        account = "DataIngestion"
        container_name = "assets"

        # cap timeout to 5 minutes
        if timeout > 300:
            timeout = 300

        result = {
            "old_blob": old_blob_name,
            "new_blob": new_blob_name,
            "copy_status": None,
            "delete_status": None,
            "message": ""
        }

        # Validate storage account
        if not set([account]).issubset(set(ACCOUNT.__args__)):
            msg = (
                f"Account parameter must be set to one of the allowed values "
                f"defined by ACCOUNT literal: {ACCOUNT.__args__}"
            )
            logger.error(msg)
            result["delete_status"] = "failed"
            result["message"] = msg
            return result

        old_blob_con_string = _get_blob_sas_uri(api_inputs=api_inputs, container=container_name, blobName=old_blob_name, account=account, can_delete=True)
        old_blob_client = BlobClient.from_blob_url(old_blob_con_string)

        new_blob_con_string = _get_blob_sas_uri(api_inputs=api_inputs, container=container_name, blobName=new_blob_name, account=account, can_write=True, can_delete=True)
        new_blob_client = BlobClient.from_blob_url(new_blob_con_string)

        # check destination doesn't already exist
        if _retry_operation(lambda: new_blob_client.exists()):
            result["copy_status"] = 'failed'
            result["message"] = f"Destination blob '{new_blob_name}' already exists."
            logger.error(result["message"])
            return result

        # wait until copy operation completes or timeout
        copy_props = _retry_operation(lambda: new_blob_client.start_copy_from_url(old_blob_client.url))
        copy_id = copy_props.get("copy_id") if isinstance(copy_props, dict) else copy_props["copy_id"]
       
        poll_interval = 2
        max_attempts = timeout // poll_interval
        logger.info(f"Started copy operation from '{old_blob_name}' to '{new_blob_name}' (CopyId={copy_id})")

        for attempt in range(max_attempts):
            props = _retry_operation(lambda: new_blob_client.get_blob_properties())
            status = props.copy.status.lower()

            if status in ("success", "failed", "aborted"):
                logger.info(f"Copy status: {status} (elapsed={attempt * poll_interval}s)")
                break

            logger.debug(f"Copy in progress. Status: {status}... elapsed={attempt * poll_interval}s")
            time.sleep(poll_interval)
        else:
            # Timeout reached. Abort copy.
            _retry_operation(lambda: new_blob_client.abort_copy(copy_id))
            result["copy_status"] = "timeout"
            result["message"] = (
                f"Copy operation wait time exceeded {timeout} seconds. "
                f"Please check manually if '{new_blob_name}' was copied successfully."
            )
            logger.warning(result["message"])
            return result


        # cleanup when copy failed/aborted, return result
        if status != "success":
            try:
                _retry_operation(lambda: new_blob_client.delete_blob())
                logger.info(f"Cleaned up failed copy blob '{new_blob_name}'.")
            except AzureError:
                logger.warning(f"Cleanup failed for '{new_blob_name}' (may not exist).")

            result["copy_status"] = status
            result["message"] = f"Blob copy failed with status: {status}"
            return result


        result["copy_status"] = "success"

        try:
            _retry_operation(lambda: old_blob_client.delete_blob())
            result["delete_status"] = "success"
            result["message"] = f"Blob renamed from '{old_blob_name}' to '{new_blob_name}'."
            logger.info(result["message"])
        except ResourceNotFoundError:
            result["delete_status"] = "skipped"
            result["message"] = f"Old blob '{old_blob_name}' was already deleted."
        except AzureError as e:
            result["delete_status"] = "failed"
            result["message"] = (
                f"Copy succeeded but deletion of old blob '{old_blob_name}' failed: {str(e)}"
            )
            logger.error(result["message"])

        return result

    @staticmethod
    def _delete(api_inputs: ApiInputs, blob_name: str, timeout: int = 60):
        """
        Deletes a blob from Azure Blob Storage.
        Restricted to work on the 'DataIngestion' Storage Account and 'assets' Container.

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by the `initialize()` function containing connection info.
        blob_name : str
            Full name (path) of the blob to delete (e.g., "folder1/folder2/file.csv").
        timeout : int, optional
            Maximum number of seconds to wait for the delete operation before aborting.
            Default is 60 seconds (1 minute). Capped at 300 seconds (5 minutes).

        Returns
        -------
        dict
            Dictionary containing the result of the delete operation with keys:
            - blob_name (str): The target blob name.
            - delete_status (str): "success", "not_found", "failed", or "timeout".
            - message (str): Summary of the operation result.
        """

        account = "DataIngestion"
        container_name = "assets"

        # Cap timeout to 5 minutes
        if timeout > 300:
            timeout = 300

        result = {
            "blob_name": blob_name,
            "delete_status": None,
            "message": ""
        }

        # Validate storage account
        if not set([account]).issubset(set(ACCOUNT.__args__)):
            msg = (
                f"Account parameter must be set to one of the allowed values "
                f"defined by ACCOUNT literal: {ACCOUNT.__args__}"
            )
            logger.error(msg)
            result["delete_status"] = "failed"
            result["message"] = msg
            return result

        # Get blob client with delete permissions
        blob_sas_uri = _get_blob_sas_uri(
            api_inputs=api_inputs,
            container=container_name,
            blobName=blob_name,
            account=account,
            can_delete=True
        )
        blob_client = BlobClient.from_blob_url(blob_sas_uri)

        # Check if blob exists before attempting deletion
        exists = _retry_operation(lambda: blob_client.exists())
        if not exists:
            result["delete_status"] = "not_found"
            result["message"] = f"Blob '{blob_name}' does not exist or was already deleted."
            logger.warning(result["message"])
            return result

        logger.info(f"Starting deletion for blob '{blob_name}' with timeout={timeout}s")

        start_time = time.time()
        try:
            _retry_operation(lambda: blob_client.delete_blob())

            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(
                    f"Deletion of blob '{blob_name}' exceeded {timeout} seconds."
                )

            result["delete_status"] = "success"
            result["message"] = f"Blob '{blob_name}' successfully deleted."
            logger.info(result["message"])

        except ResourceNotFoundError:
            result["delete_status"] = "not_found"
            result["message"] = f"Blob '{blob_name}' was not found during deletion."
            logger.warning(result["message"])

        except TimeoutError as te:
            result["delete_status"] = "timeout"
            result["message"] = str(te)
            logger.warning(result["message"])

        except AzureError as e:
            result["delete_status"] = "failed"
            result["message"] = f"Failed to delete blob '{blob_name}': {str(e)}"
            logger.error(result["message"])

        return result

    @staticmethod
    def _list_files(api_inputs: ApiInputs, account: ACCOUNT, container_name: str, folder_path: str, timeout: int = 60):
        """
        Lists all blobs (files) under a specified folder path within Blob storage account and container passed.

        Parameters
        ----------
        api_inputs : ApiInputs
            Object returned by the `initialize()` function containing connection info.
        account : ACCOUNT
            Must be one of the allowed storage accounts defined by the ACCOUNT Literal.
        container_name : str
            The name of the container to list blobs from.
        folder_path : str
            Path prefix (virtual folder) whose contents should be listed.
            Example: "raw-data/2025/10/06/" or "processed/".
            Must not start with a leading slash ('/').
        timeout : int, optional
            Maximum number of seconds to wait for the listing operation before aborting.
            Default is 60 seconds (1 minute). Capped at 300 seconds (5 minutes).

        Returns
        -------
        dict
            Dictionary containing the result of the listing operation with keys:
            - account (str): The target storage account.
            - container (str): The target container.
            - folder_path (str): The folder (prefix) queried.
            - file_count (int): Number of blobs found under the prefix.
            - files (list[str]): List of blob names.
            - status (str): "success", "empty", "timeout", or "failed".
            - message (str): Summary of the operation result.
        """

        # Cap timeout to 5 minutes
        if timeout > 300:
            timeout = 300

        result = {
            "account": account,
            "container": container_name,
            "folder_path": folder_path,
            "file_count": 0,
            "files": [],
            "status": None,
            "message": ""
        }

        if not set([account]).issubset(set(ACCOUNT.__args__)):
            valid_accounts = ACCOUNT.__args__
            msg = (
                f"Invalid storage account '{account}'. "
                f"Must be one of the allowed values defined by ACCOUNT literal: {valid_accounts}"
            )
            logger.error(msg)
            result["status"] = "failed"
            result["message"] = msg
            return result

        if not all([account, container_name, folder_path]):
            msg = "Parameters 'account', 'container_name', and 'folder_path' must all be non-empty."
            logger.error(msg)
            result["status"] = "failed"
            result["message"] = msg
            return result

        # Normalize (avoid leading slash)
        folder_path = folder_path.lstrip("/")

        try:
            container_sas_uri = _get_container_sas_uri(
                api_inputs=api_inputs,
                container=container_name,
                account=account
            )
            container_client = ContainerClient.from_container_url(container_sas_uri)

            start_time = time.time()
            logger.info(f"Listing blobs in '{account}/{container_name}/{folder_path}' with timeout={timeout}s")

            def _list_operation():
                return list(container_client.list_blobs(name_starts_with=folder_path))

            blobs = _retry_operation(_list_operation)

            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Listing operation exceeded {timeout} seconds.")

            if not blobs:
                result["status"] = "empty"
                result["message"] = f"No blobs found under prefix '{folder_path}' in container '{container_name}'."
                logger.warning(result["message"])
                return result

            blob_names = [b.name for b in blobs]
            result["files"] = blob_names
            result["file_count"] = len(blob_names)
            result["status"] = "success"
            result["message"] = f"Found {len(blob_names)} blob(s) under folder '{folder_path}'."
            logger.info(result["message"])

        except TimeoutError as te:
            result["status"] = "timeout"
            result["message"] = str(te)
            logger.warning(result["message"])

        except AzureError as e:
            result["status"] = "failed"
            result["message"] = f"Azure error during blob listing: {str(e)}"
            logger.error(result["message"])

        except Exception as e:
            result["status"] = "failed"
            result["message"] = f"Unexpected error during blob listing: {str(e)}"
            logger.exception(result["message"])

        return result



    @staticmethod
    def _guide_blob_upload(api_inputs: ApiInputs, local_folder_path: str, driver_id: uuid.UUID):
        """Upload folder files to Guides' blob storage.

        Returns
        -------

        """
        account = "DataIngestion"
        container_name = "guides-form"
        blob_prefix = driver_id + "/"

        # Get a reference to the container
        container_con_string = _get_container_sas_uri(api_inputs, container_name, account, True)
        container_client = ContainerClient.from_container_url(container_con_string)

        # Get a list of files in the local folder
        files = [f for f in os.listdir(local_folder_path) if os.path.isfile(
            os.path.join(local_folder_path, f))]

        try:
            # Upload each file to storage
            for root, _, files in os.walk(local_folder_path):
                for file_name in files:
                    local_file_path = os.path.join(root, file_name)
                    blob_name = blob_prefix + os.path.relpath(local_file_path, local_folder_path).replace(
                        os.path.sep, "/")

                    with open(local_file_path, "rb") as data:
                        container_client.upload_blob(name=blob_name, data=data, content_settings=ContentSettings(
                            content_type='application/octet-stream'), overwrite=True)

                    logger.info(f"Uploaded {local_file_path} to {blob_name}")

            return True
        except Exception as exc:
            logger.exception(str(exc))
            return False

def _retry_operation(func, retries=3, base_delay=1, max_delay=16):
    """
    Retry helper with exponential backoff.
    """
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            if attempt == retries - 1:
                raise  # final failure
            delay = min(max_delay, base_delay * (2 ** attempt)) + random.uniform(0, 0.5)
            time.sleep(delay)


def _get_ingestion_service_bus_connection_string(api_inputs: ApiInputs, queue_type: str = 'DataIngestion'):
    """
    Get connection string specific to Data Ingestion Service Bus

    Parameters
    ----------
    api_inputs : ApiInputs
            Object returned by initialize() function.

    Returns
    -------
    str
        Data Ingestion Service Bus connection string
    """
    headers = api_inputs.api_headers.default

    if not queue_type or queue_type == '':
        queue_type = 'DataIngestion'

    params = {'serviceBusType': queue_type}

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/data-ingestion/data-feed/service-bus"
    response = requests.request("GET", url, timeout=20, headers=headers, params=params)

    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return None
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return None

    return response.text


def _get_container_sas_uri(api_inputs: ApiInputs, container: str, account: ACCOUNT = 'SwitcStorage', writable: bool = False):
    """
    Get container connection string from specified Storage Account

    Parameters
    ----------
    api_inputs : ApiInputs
            Object returned by initialize() function.
    container: str
        Name of the container under the account specified
    account : ACCOUNT, default = 'SwitchStorage'x
         (Default value = 'SwitchStorage')
    writable: bool
        Sets permissions expectation for the generated SAS Uri

    Returns
    -------
    str
        container SAS URI connection string
    """

    if container == None or len(container) == 0:
        logger.error('Must set a container to get Container connection string.')
        return ""

    headers = api_inputs.api_headers.default
    expire_after_hours = 1

    payload = {
        "storageOptions": __get_storage_options(account),
        "containerName": container,
        "expireAfterHours": expire_after_hours,
        "isWritable": writable
    }

    url = f"{api_inputs.api_base_url}/blob/container-sas"
    response = requests.request("POST", url, json=payload, headers=headers)

    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return ""
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return ""

    return response.text

def _get_blob_sas_uri(api_inputs: ApiInputs, container: str, blobName: str, account: ACCOUNT = 'SwitcStorage', can_write: bool = False, can_delete: bool = False):
    """
    Get blob connection string from specified Storage Account

    Parameters
    ----------
    api_inputs : ApiInputs
            Object returned by initialize() function.
    container: str
        Name of the container under the account specified
    account : ACCOUNT, default = 'SwitchStorage'x
         (Default value = 'SwitchStorage')
    blobName: str
        The blob path to create SAS Uri

    Returns
    -------
    str
        blob SAS URI connection string
    """

    if container == None or len(container) == 0:
        logger.error('Must set a container to get Container connection string.')
        return ""
    
    if blobName == None or len(blobName) == 0:
        logger.error('BlobName cannot be empty.')
        return ""

    headers = api_inputs.api_headers.default
    expire_after_hours = 1

    payload = {
        "storageOptions": __get_storage_options(account),
        "containerName": container,
        "blobName": blobName,
        "expireAfterHours": expire_after_hours,
        "canWrite": can_write,
        "canDelete": can_delete
    }

    url = f"{api_inputs.api_base_url}/blob/blob-sas"
    response = requests.request("POST", url, json=payload, headers=headers)

    if response.status_code != 200:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return ""
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s', response.request.url)
        return ""

    return response.text


def _get_structure(df):
    """Get dataframe structure

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------

    """

    a = df.dtypes
    a = pandas.Series(a)
    a = a.reset_index().rename(columns={0: 'dtype'})
    a['dtype'] = a['dtype'].astype('str')
    a.set_index('index', inplace=True)
    a = a.to_dict()
    return a['dtype']


def __get_storage_options(account: ACCOUNT):
    """
    Get Storage Account Options. Currently the existing account literal doesn't match the Enum equivalent of storage
    options in the API, so we have this method

    Parameters
    ----------
    account : ACCOUNT
        Account to map API storage account options

    Returns
    -------
    str
        API equivalent account storage name
    """

    if account == None or len(account) == 0:
        logger.error('Mapping to storage options requires Account Parameter Value.')
        return account

    if account == 'SwitchStorage':
        return 'LegacySwitchStorage'
    elif account == 'SwitchContainer':
        return 'LegacySwitchContainer'
    elif account == 'Argus':
        return 'ArgusStorage'
    elif account == 'DataIngestion':
        return 'DataIngestionStorage'
    elif account == 'SwitchGuides':
        return 'DataIngestionStorage'

    return account
