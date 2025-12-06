# Azure Blob Storage Setup Instructions

This guide will walk you through setting up Azure Blob Storage for the AI Assistant backend.

## Prerequisites

- An active Azure subscription
- Azure CLI installed (optional, but recommended)

---

## Option 1: Azure Portal Setup

### Step 1: Create a Storage Account

1. **Navigate to Azure Portal**
   - Go to [https://portal.azure.com](https://portal.azure.com)
   - Sign in with your Azure account

2. **Create Storage Account**
   - Click `+ Create a resource`
   - Search for "Storage account" and select it
   - Click `Create`

3. **Configure Basic Settings**
   - **Subscription**: Select your Azure subscription
   - **Resource Group**: Create new or select existing (e.g., `ai-assistant-rg`)
   - **Storage account name**: Enter a unique name (e.g., `aiassistantstorage123`)
     - Must be 3-24 characters, lowercase letters and numbers only
     - Must be globally unique across Azure
   - **Region**: Choose a region close to your users (e.g., `East US`)
   - **Performance**: Select `Standard`
   - **Redundancy**: Select `Locally-redundant storage (LRS)` (cheapest option for dev/test)

4. **Advanced Settings** (Optional)
   - Leave defaults or adjust as needed
   - For development, you can disable secure transfer if needed (not recommended for production)

5. **Review + Create**
   - Click `Review + create`
   - Review your settings
   - Click `Create`
   - Wait for deployment to complete (~1-2 minutes)

### Step 2: Get Connection String

1. **Navigate to Storage Account**
   - Go to your newly created storage account
   - In the left menu, under `Security + networking`, click `Access keys`

2. **Copy Connection String**
   - Under `key1`, click `Show` next to the connection string
   - Click the copy icon to copy the entire connection string
   - Save this for later - you'll need it for your `.env` file

   Example format:
   ```
   DefaultEndpointsProtocol=https;AccountName=aiassistantstorage123;AccountKey=ABC123...==;EndpointSuffix=core.windows.net
   ```

### Step 3: Create Container (Optional)

The application will automatically create the container `ai-assistant-data` if it doesn't exist. However, you can create it manually:

1. **Navigate to Containers**
   - In your storage account, click `Containers` under `Data storage`
   - Click `+ Container`

2. **Create Container**
   - **Name**: `ai-assistant-data`
   - **Public access level**: `Private (no anonymous access)`
   - Click `Create`

---

## Option 2: Azure CLI Setup

If you prefer using the command line:

```bash
# Login to Azure
az login

# Set variables
RESOURCE_GROUP="ai-assistant-rg"
LOCATION="eastus"
STORAGE_ACCOUNT="aiassistantstorage123"  # Change to your unique name
CONTAINER_NAME="ai-assistant-data"

# Create resource group (if it doesn't exist)
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create storage account
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS \
  --kind StorageV2

# Get connection string
az storage account show-connection-string \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --output tsv

# Create container (optional - app will auto-create)
az storage container create \
  --name $CONTAINER_NAME \
  --account-name $STORAGE_ACCOUNT
```

---

## Step 4: Configure Your Application

1. **Copy Environment Template**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edit `.env` File**
   - Open `backend/.env` in your editor
   - Replace the placeholder values:

   ```bash
   # Azure Blob Storage Configuration
   BLOB_CONNECTION_STRING=<paste-your-connection-string-here>
   BLOB_CONTAINER_NAME=ai-assistant-data
   
   # Ollama Configuration
   OLLAMA_URL=http://ollama-service:11434
   
   # Optional: Application Settings
   LOG_LEVEL=INFO
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Test the Connection**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

   The application should start without errors. Check the logs for:
   ```
   INFO: Container 'ai-assistant-data' initialized
   ```

---

## Verify Setup

### Using Azure Portal

1. Navigate to your storage account
2. Click `Containers`
3. Click `ai-assistant-data`
4. After running the application and creating a session, you should see:
   - `sessions/` directory with session JSON files
   - `messages/` directory with message JSON files
   - `metadata/` directory with metadata JSON files

### Using Azure Storage Explorer

1. Download [Azure Storage Explorer](https://azure.microsoft.com/en-us/products/storage/storage-explorer/)
2. Connect using your connection string
3. Browse the `ai-assistant-data` container
4. View the blob hierarchy and JSON contents

---

## Cost Estimation

For development/testing with low traffic:

- **Storage**: ~$0.018/GB/month (Hot tier)
- **Operations**: ~$0.004 per 10,000 write operations
- **Estimated monthly cost**: $5-10 for typical usage

This is significantly cheaper than Cosmos DB (~$70/month).

---

## Troubleshooting

### Connection String Issues

**Error**: `ValueError: BLOB_CONNECTION_STRING environment variable must be set`

**Solution**: Ensure your `.env` file exists and contains the connection string.

### Container Creation Fails

**Error**: `Container creation failed`

**Solution**: 
- Check that your storage account name is correct
- Verify your connection string is valid
- Ensure you have proper permissions on the storage account

### Authentication Errors

**Error**: `403 Forbidden` or authentication errors

**Solution**:
- Regenerate your access key in Azure Portal
- Update the connection string in your `.env` file
- Ensure the connection string includes the `AccountKey` parameter

---

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Rotate access keys regularly** (every 90 days recommended)
3. **Use Azure Key Vault** for production environments
4. **Enable firewall rules** to restrict access to specific IPs
5. **Enable soft delete** to recover accidentally deleted data

---

## Migration from Cosmos DB

If you're migrating from an existing Cosmos DB setup:

### Export Data from Cosmos DB

```python
# Run this script to export your Cosmos DB data
from app.cosmos_client import get_cosmos_client
from app.blob_client import get_blob_client
import json

cosmos = get_cosmos_client()
blob = get_blob_client()

# Export sessions
sessions = cosmos.query_items("sessions", "SELECT * FROM c")
for session in sessions:
    blob_path = f"sessions/{session['session_id']}.json"
    blob.upload_json(blob_path, session)

# Export messages
messages = cosmos.query_items("messages", "SELECT * FROM c")
for message in messages:
    blob_path = f"messages/{message['session_id']}/{message['message_id']}.json"
    blob.upload_json(blob_path, message)

# Export metadata
metadata = cosmos.query_items("metadata", "SELECT * FROM c")
for meta in metadata:
    blob_path = f"metadata/{meta['session_id']}.json"
    blob.upload_json(blob_path, meta)

print("Migration complete!")
```

### Clean Up Cosmos DB Resources

Once you've verified the migration:

1. Navigate to your Cosmos DB account in Azure Portal
2. Click `Delete` to remove the account
3. This will stop all charges for Cosmos DB

---

## Next Steps

- Test all API endpoints to ensure functionality
- Monitor blob storage usage in Azure Portal
- Set up alerts for storage costs
- Consider implementing data retention policies
