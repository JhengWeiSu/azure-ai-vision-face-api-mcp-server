import os

from azure.storage.blob import ContainerClient

from .utils._enums import ListBlobFoldersConfig, DownloadBlobFolderConfig
from typing import Annotated
from pydantic import Field


def list_blob_folders_and_choose() -> str:
    """
    Lists all top-level folders (virtual directories) in the Azure Blob container and asks the user to choose one for enrollment.
    """
    account = os.getenv("AZURE_STORAGE_ACCOUNT")
    container = os.getenv("AZURE_STORAGE_CONTAINER")
    sas_token = os.getenv("AZURE_STORAGE_SAS_TOKEN")

    if not all([account, container, sas_token]):
        return "Missing required environment variables: AZURE_STORAGE_ACCOUNT, AZURE_STORAGE_CONTAINER, AZURE_STORAGE_SAS_TOKEN"

    account_url = f"https://{account}.blob.core.windows.net"
    container_client = ContainerClient(
        account_url, container_name=container, credential=sas_token
    )

    blob_list = container_client.walk_blobs(delimiter="/")
    folders = [b.name.rstrip("/") for b in blob_list if b.name.endswith("/")]

    if not folders:
        return "No folders found in the container."

    folder_list_str = "\n".join(f"- {folder}" for folder in folders)
    return ListBlobFoldersConfig.PROMPT_CHOOSE_FOLDER.format(
        folder_list=folder_list_str
    )


def download_blob_folder_from_container(
    folder_name: Annotated[
        str, Field(description=DownloadBlobFolderConfig.ARGS_FOLDER_NAME)
    ],
    local_dir: Annotated[
        str, Field(description=DownloadBlobFolderConfig.ARGS_LOCAL_DIR)
    ] = "./downloaded_images",
) -> str:
    """
    Downloads all blobs (files) from the specified folder in the Azure Blob container to a local directory,
    preserving the same subfolder structure as in the storage.
    """
    account = os.getenv("AZURE_STORAGE_ACCOUNT")
    container = os.getenv("AZURE_STORAGE_CONTAINER")
    sas_token = os.getenv("AZURE_STORAGE_SAS_TOKEN")

    if not all([account, container, sas_token]):
        return "Missing required environment variables: AZURE_STORAGE_ACCOUNT, AZURE_STORAGE_CONTAINER, AZURE_STORAGE_SAS_TOKEN"

    account_url = f"https://{account}.blob.core.windows.net"
    container_client = ContainerClient(
        account_url, container_name=container, credential=sas_token
    )

    blobs = container_client.list_blobs(name_starts_with=folder_name + "/")
    downloaded_files = []
    for blob in blobs:
        if blob.name.endswith("/"):
            continue
        normalized_folder = folder_name.rstrip("/") + "/"
        rel_path = blob.name[len(normalized_folder) :]
        local_path = os.path.join(local_dir, rel_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            data = container_client.download_blob(blob.name)
            f.write(data.readall())
        downloaded_files.append(local_path)

    if not downloaded_files:
        return f"No files found in folder '{folder_name}'."
    return DownloadBlobFolderConfig.RESULT_SUCCESS.format(
        num_files=len(downloaded_files),
        folder_name=folder_name,
        local_dir=local_dir,
        file_list="\n".join(downloaded_files),
    )
