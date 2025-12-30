import os
from azure.storage.blob import BlobServiceClient
from src.helper.auth import get_credential

STORAGE_CONTAINER = "azure-network-backups"
STORAGE_ACCOUNT_NAME = "blob"


def upload_to_blob(zip_buffer, blob_name: str):
    """
    Upload ZIP file to Azure Blob Storage using Azure AD authentication.
    """
    credential = get_credential()

    if not STORAGE_ACCOUNT_NAME:
        raise EnvironmentError("AZURE_STORAGE_ACCOUNT_NAME not set")

    print(f"\nUploading to Azure Blob Storage using Azure AD...")
    account_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
    blob_service = BlobServiceClient(account_url=account_url, credential=credential)

    # Ensure container exists
    container_client = blob_service.get_container_client(STORAGE_CONTAINER)
    try:
        container_client.create_container()
        print(f"Created container: {STORAGE_CONTAINER}")
    except Exception:
        pass

    container_client.upload_blob(blob_name, zip_buffer.getvalue(), overwrite=True)
    print(f"Uploaded: {blob_name}")
