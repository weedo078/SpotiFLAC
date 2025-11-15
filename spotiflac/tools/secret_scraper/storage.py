"""Secret storage management."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List
import json


class SecretStorageError(Exception):
    """Raised when secret storage operations fail."""
    pass


class SecretStorage:
    """Manage storage of Spotify secrets.
    
    Handles reading and writing secrets to JSON files.
    
    Example:
        >>> storage = SecretStorage()
        >>> storage.save_secrets([{"version": 1, "secret": [...]}])
        >>> secrets = storage.load_secrets()
    """
    
    DEFAULT_PATH = Path.home() / ".spotify-secret" / "secretBytes.json"
    
    def __init__(self, *, storage_path: Path = None):
        """Initialize secret storage.
        
        Args:
            storage_path: Optional custom storage path
        """
        self.storage_path = storage_path or self.DEFAULT_PATH
    
    def save_secrets(self, secrets: List[Dict[str, Any]]) -> None:
        """Save secrets to JSON file.
        
        Args:
            secrets: List of secret dictionaries
            
        Raises:
            SecretStorageError: If saving fails
        """
        try:
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write JSON
            with open(self.storage_path, 'w') as f:
                json.dump(secrets, f, indent=2)
                
        except Exception as e:
            raise SecretStorageError(f"Failed to save secrets: {e}")
    
    def load_secrets(self) -> List[Dict[str, Any]]:
        """Load secrets from JSON file.
        
        Returns:
            List of secret dictionaries
            
        Raises:
            SecretStorageError: If loading fails or file doesn't exist
        """
        if not self.storage_path.exists():
            raise SecretStorageError(f"Secret file not found: {self.storage_path}")
        
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise SecretStorageError(f"Failed to load secrets: {e}")
    
    def process_captured_secrets(
        self,
        captured_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process captured secrets into storage format.
        
        Args:
            captured_data: Raw captured data from browser
            
        Returns:
            Processed secrets ready for storage
        """
        processed = []
        
        for item in captured_data:
            # Extract version and secret from captured data
            version = item.get('version')
            secret = item.get('secret')
            
            if version is not None and secret is not None:
                processed.append({
                    'version': version,
                    'secret': secret
                })
        
        return processed


__all__ = [
    "SecretStorage",
    "SecretStorageError",
]
