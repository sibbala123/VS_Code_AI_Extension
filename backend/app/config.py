from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
import logging

logger = logging.getLogger(__name__)

class Config:
    """Configuration class that retrieves secrets from Azure Key Vault or environment variables"""
    
    def __init__(self):
        self.key_vault_name = os.getenv("KEY_VAULT_NAME")
        
        if self.key_vault_name:
            # Use Key Vault
            logger.info(f"Initializing configuration from Key Vault: {self.key_vault_name}")
            self._init_key_vault()
        else:
            # Fallback to environment variables (for local development)
            logger.warning("KEY_VAULT_NAME not set, using environment variables for configuration")
            self._init_from_env()
    
    def _init_key_vault(self):
        """Initialize Key Vault client and retrieve secrets"""
        try:
            credential = DefaultAzureCredential()
            vault_url = f"https://{self.key_vault_name}.vault.azure.net"
            client = SecretClient(vault_url=vault_url, credential=credential)
            
            # Retrieve secrets
            logger.info("Retrieving secrets from Key Vault...")
            self.blob_connection_string = client.get_secret("blob-connection-string").value
            self.blob_container_name = client.get_secret("blob-container-name").value
            self.ollama_url = client.get_secret("ollama-url").value
            
            logger.info(f"Successfully retrieved secrets from Key Vault: {self.key_vault_name}")
        except Exception as e:
            logger.error(f"Failed to retrieve secrets from Key Vault: {e}")
            logger.warning("Falling back to environment variables")
            self._init_from_env()
    
    def _init_from_env(self):
        """Initialize configuration from environment variables"""
        self.blob_connection_string = os.getenv("BLOB_CONNECTION_STRING")
        self.blob_container_name = os.getenv("BLOB_CONTAINER_NAME", "ai-assistant-data")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://ollama-service:11434")
        
        if not self.blob_connection_string:
            logger.error("BLOB_CONNECTION_STRING not found in environment variables")
            raise ValueError("BLOB_CONNECTION_STRING must be set in environment or Key Vault")


# Singleton instance
_config = None


def get_config() -> Config:
    """Get or create the configuration singleton"""
    global _config
    if _config is None:
        _config = Config()
    return _config
