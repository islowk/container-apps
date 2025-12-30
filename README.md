# Azure Network Backup - Container Apps

Containerized Azure network resource backup service for Azure Container Apps, triggered by Azure Logic Apps.

## Quick Start

1. Update `deploy.sh` with your configuration
2. Run `./deploy.sh`
3. Configure Logic App to call the endpoint
4. Done!

## Deployment

### Prerequisites
- Azure CLI installed and authenticated
- Service Principal with proper permissions

### Configure and Deploy

Edit `deploy.sh`:
```bash
RESOURCE_GROUP="rg-network-backup-prod"
ACR_NAME="acrnetworkbackup"
AZURE_CLIENT_ID="your-sp-client-id"
AZURE_TENANT_ID="your-tenant-id"
AZURE_STORAGE_ACCOUNT_NAME="your-storage-account"
```

Run deployment:
```bash
chmod +x deploy.sh
./deploy.sh
```

## Logic App Integration

### Option A: Backup All Subscriptions

**HTTP Action Configuration:**
- **Method**: `POST` or `GET`
- **URI**: `https://your-app.azurecontainerapps.io/network_backup_trigger`
- **Body**: Leave empty

### Option B: Backup Specific Subscription

You have **three ways** to specify the target subscription:

#### Method 1: Query Parameter (Simplest)
**HTTP Action Configuration:**
- **Method**: `POST` or `GET`
- **URI**: `https://your-app.azurecontainerapps.io/network_backup_trigger?target_sub=Production`

Or with Subscription ID:
- **URI**: `https://your-app.azurecontainerapps.io/network_backup_trigger?target_sub=12345678-1234-1234-1234-123456789abc`

#### Method 2: JSON Body
**HTTP Action Configuration:**
- **Method**: `POST`
- **URI**: `https://your-app.azurecontainerapps.io/network_backup_trigger`
- **Headers**: `Content-Type: application/json`
- **Body**:

Using Subscription ID:
```json
{
  "target_sub": "12345678-1234-1234-1234-123456789abc"
}
```

Or using Subscription Name:
```json
{
  "target_sub": "Production"
}
```

#### Method 3: Form Data
**HTTP Action Configuration:**
- **Method**: `POST`
- **URI**: `https://your-app.azurecontainerapps.io/network_backup_trigger`
- **Headers**: `Content-Type: application/x-www-form-urlencoded`
- **Body**: `target_sub=Production`

**💡 Recommendation**: Use **Method 1 (Query Parameter)** - it's the simplest for Logic Apps and doesn't require setting headers or body.

### Expected Response

Success:
```json
{
  "timestamp": "2024-12-30_143025",
  "status": "success",
  "subscriptions": [
    {
      "subscription_id": "sub-id",
      "display_name": "Production",
      "backup_blob": "2024-12-30_143025/production_network_backup.zip"
    }
  ],
  "message": "Backup completed successfully for 1 subscription(s)!"
}
```

Failure:
```json
{
  "timestamp": "2024-12-30_143025",
  "status": "failed",
  "subscriptions": [],
  "message": "Fatal error: Permission denied"
}
```

## Storage Structure

```
azure-network-backups/
└── 2024-12-30_143025/
    ├── sub1_network_backup.zip
    └── sub2_network_backup.zip
```

## Local Testing

```bash
docker build -t azure-network-backup:local .
docker run -p 8080:8080 \
  -e AZURE_CLIENT_ID="..." \
  -e AZURE_CLIENT_SECRET="..." \
  -e AZURE_TENANT_ID="..." \
  -e AZURE_STORAGE_ACCOUNT_NAME="..." \
  azure-network-backup:local
```

## Monitoring

```bash
# View logs
az containerapp logs show --name ca-network-backup --resource-group rg-network-backup-prod --follow

# Check status
az containerapp show --name ca-network-backup --resource-group rg-network-backup-prod
```

## Cost
- Scale to zero when idle
- ~$0.05/month for monthly backups
-