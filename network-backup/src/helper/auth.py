import os
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import SubscriptionClient
from azure.storage.blob import BlobServiceClient

def get_credential():
    """
    Returns Azure credential.
    """
    required_vars = ["AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID"]
    if all(os.getenv(v) for v in required_vars):
        print("Using Service Principal authentication")
        return ClientSecretCredential(
            client_id=os.environ["AZURE_CLIENT_ID"],
            client_secret=os.environ["AZURE_CLIENT_SECRET"],
            tenant_id=os.environ["AZURE_TENANT_ID"]
        )

def preflight_check():
    """
    Validate Service Principal permissions for Azure resources before running backup.
    """
    # Check environment variables
    required_vars = ["AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID", "AZURE_STORAGE_ACCOUNT_NAME"]
    missing_vars = [v for v in required_vars if not os.getenv(v)]
    if missing_vars:
        raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")

    credential = ClientSecretCredential(
        client_id=os.environ["AZURE_CLIENT_ID"],
        client_secret=os.environ["AZURE_CLIENT_SECRET"],
        tenant_id=os.environ["AZURE_TENANT_ID"]
    )

    # Check subscription access
    try:
        sub_client = SubscriptionClient(credential)
        subs = list(sub_client.subscriptions.list())
        if not subs:
            raise PermissionError("No subscriptions accessible with this Service Principal.")
        print(f"Subscription access verified ({len(subs)} subscriptions).")
    except Exception as e:
        raise PermissionError(f"Failed to list subscriptions: {str(e)}")

    # Check storage access
    try:
        account_url = f"https://{os.environ['AZURE_STORAGE_ACCOUNT_NAME']}.blob.core.windows.net"
        blob_service = BlobServiceClient(account_url=account_url, credential=credential)
        container_client = blob_service.get_container_client("network-backups")
        container_client.get_container_properties()  # Will fail if no access
        print("Storage access verified.")
    except Exception as e:
        raise PermissionError(f"Failed to access storage container: {str(e)}")
