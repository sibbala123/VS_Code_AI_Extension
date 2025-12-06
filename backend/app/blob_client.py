from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
import json
from typing import Optional, List, Dict, Any
import logging

from .config import get_config

logger = logging.getLogger(__name__)


class BlobStorageClient:
    """Wrapper class for Azure Blob Storage client"""
    
    def __init__(self):
        """Initialize Blob Storage client with configuration from Key Vault or environment"""
        config = get_config()
        self.connection_string = config.blob_connection_string
        self.container_name = config.blob_container_name
        
        if not self.connection_string:
            raise ValueError("Blob connection string not found in configuration")
        
        # Initialize client
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = None
        
        # Initialize container
        self._initialize_container()
    
    def _initialize_container(self):
        """Create container if it doesn't exist"""
        try:
            self.container_client = self.blob_service_client.get_container_client(self.container_name)
            
            # Create container if it doesn't exist
            if not self.container_client.exists():
                self.container_client.create_container()
                logger.info(f"Container '{self.container_name}' created")
            else:
                logger.info(f"Container '{self.container_name}' already exists")
                
        except Exception as e:
            logger.error(f"Error initializing container: {str(e)}")
            raise
    
    def upload_json(self, blob_path: str, data: Dict[str, Any]) -> None:
        """
        Upload JSON data to a blob
        
        Args:
            blob_path: Path to the blob (e.g., 'sessions/session-id.json')
            data: Dictionary to be stored as JSON
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_path)
            json_data = json.dumps(data, default=str)  # default=str handles datetime serialization
            blob_client.upload_blob(json_data, overwrite=True)
            logger.info(f"Uploaded blob: {blob_path}")
        except Exception as e:
            logger.error(f"Error uploading blob {blob_path}: {str(e)}")
            raise
    
    def download_json(self, blob_path: str) -> Optional[Dict[str, Any]]:
        """
        Download JSON data from a blob
        
        Args:
            blob_path: Path to the blob
            
        Returns:
            Dictionary containing the JSON data, or None if blob doesn't exist
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_path)
            
            if not blob_client.exists():
                logger.warning(f"Blob not found: {blob_path}")
                return None
            
            blob_data = blob_client.download_blob().readall()
            data = json.loads(blob_data)
            logger.info(f"Downloaded blob: {blob_path}")
            return data
            
        except Exception as e:
            logger.error(f"Error downloading blob {blob_path}: {str(e)}")
            raise
    
    def delete_blob(self, blob_path: str) -> None:
        """
        Delete a blob
        
        Args:
            blob_path: Path to the blob
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_path)
            
            if blob_client.exists():
                blob_client.delete_blob()
                logger.info(f"Deleted blob: {blob_path}")
            else:
                logger.warning(f"Blob not found for deletion: {blob_path}")
                
        except Exception as e:
            logger.error(f"Error deleting blob {blob_path}: {str(e)}")
            raise
    
    def list_blobs(self, prefix: str = "") -> List[str]:
        """
        List all blobs with a given prefix
        
        Args:
            prefix: Prefix to filter blobs (e.g., 'messages/session-id/')
            
        Returns:
            List of blob paths
        """
        try:
            blob_list = self.container_client.list_blobs(name_starts_with=prefix)
            blob_paths = [blob.name for blob in blob_list]
            logger.info(f"Listed {len(blob_paths)} blobs with prefix: {prefix}")
            return blob_paths
            
        except Exception as e:
            logger.error(f"Error listing blobs with prefix {prefix}: {str(e)}")
            raise
    
    def blob_exists(self, blob_path: str) -> bool:
        """
        Check if a blob exists
        
        Args:
            blob_path: Path to the blob
            
        Returns:
            True if blob exists, False otherwise
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_path)
            return blob_client.exists()
        except Exception as e:
            logger.error(f"Error checking blob existence {blob_path}: {str(e)}")
            return False


# Singleton instance
_blob_client: Optional[BlobStorageClient] = None


def get_blob_client() -> BlobStorageClient:
    """Get or create the Blob Storage client singleton"""
    global _blob_client
    if _blob_client is None:
        _blob_client = BlobStorageClient()
    return _blob_client
