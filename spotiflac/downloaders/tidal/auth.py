"""Tidal authentication handling."""
from __future__ import annotations

import base64
from typing import Optional, Dict, Any
import requests

from spotiflac.downloaders import DownloadError


class TidalAuthError(DownloadError):
    """Raised when Tidal authentication fails."""
    pass


class TidalAuthenticator:
    """Handle Tidal API authentication.
    
    Manages OAuth token retrieval for Tidal API access.
    
    Example:
        >>> auth = TidalAuthenticator()
        >>> token = auth.get_access_token()
    """
    
    def __init__(
        self,
        *,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        timeout: int = 30,
    ):
        """Initialize Tidal authenticator.
        
        Args:
            client_id: Optional custom client ID
            client_secret: Optional custom client secret
            timeout: Request timeout in seconds
        """
        self.client_id = client_id or self._get_default_client_id()
        self.client_secret = client_secret or self._get_default_client_secret()
        self.timeout = timeout
        self._cached_token: Optional[str] = None
    
    @staticmethod
    def _get_default_client_id() -> str:
        """Decode default client ID."""
        return base64.b64decode("NkJEU1JkcEs5aHFFQlRnVQ==").decode()
    
    @staticmethod
    def _get_default_client_secret() -> str:
        """Decode default client secret."""
        return base64.b64decode("eGV1UG1ZN25icFo5SUliTEFjUTkzc2hrYTFWTmhlVUFxTjZJY3N6alRHOD0=").decode()
    
    def get_access_token(self, api_url: str) -> str:
        """Obtain access token for API requests.
        
        Args:
            api_url: Base URL of Tidal API instance (not used for auth)
            
        Returns:
            Access token string
            
        Raises:
            TidalAuthError: If token retrieval fails
        """
        if self._cached_token:
            return self._cached_token
        
        # Use official Tidal auth server, not the proxy
        token_url = "https://auth.tidal.com/v1/oauth2/token"
        
        try:
            response = requests.post(
                token_url,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                },
                auth=(self.client_id, self.client_secret),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            token = data.get('access_token')
            
            if not token:
                raise TidalAuthError("No access token in response")
            
            self._cached_token = token
            return token
            
        except requests.exceptions.RequestException as e:
            raise TidalAuthError(f"Failed to get access token: {e}")
    
    def clear_cache(self) -> None:
        """Clear cached token."""
        self._cached_token = None


__all__ = ["TidalAuthenticator", "TidalAuthError"]
