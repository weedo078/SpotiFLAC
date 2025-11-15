"""Spotify authentication and TOTP generation."""
from __future__ import annotations

from pathlib import Path
from typing import Tuple
import requests
import json
import pyotp
import base64

from spotiflac.downloaders.deezer.utils import get_random_user_agent


class SpotifyAuthError(Exception):
    """Raised when Spotify authentication fails."""
    pass


class SpotifySecretManager:
    """Manage Spotify secrets and TOTP generation.
    
    Fetches secrets from GitHub or local cache and generates TOTP tokens.
    
    Example:
        >>> manager = SpotifySecretManager()
        >>> totp, server_time, version = manager.generate_totp()
    """
    
    GITHUB_URL = "https://raw.githubusercontent.com/afkarxyz/secretBytes/refs/heads/main/secrets/secretBytes.json"
    LOCAL_PATH = Path.home() / ".spotify-secret" / "secretBytes.json"
    
    @classmethod
    def fetch_secrets(cls, timeout: int = 10) -> Tuple[list, bool]:
        """Fetch secrets from GitHub or local cache.
        
        Args:
            timeout: Request timeout in seconds
            
        Returns:
            Tuple of (secrets_list, used_local_cache)
            
        Raises:
            SpotifyAuthError: If secrets cannot be fetched
        """
        # Try GitHub first
        try:
            resp = requests.get(cls.GITHUB_URL, timeout=timeout)
            if resp.status_code != 200:
                raise Exception(f"GitHub fetch failed with status: {resp.status_code}")
            return resp.json(), False
        except Exception as github_error:
            # Fallback to local cache
            try:
                if cls.LOCAL_PATH.exists():
                    with open(cls.LOCAL_PATH, 'r') as f:
                        return json.load(f), True
                else:
                    raise SpotifyAuthError(
                        f"GitHub failed ({github_error}) and no local file found at {cls.LOCAL_PATH}"
                    )
            except SpotifyAuthError:
                raise
            except Exception as local_error:
                raise SpotifyAuthError(
                    f"Failed to fetch secrets from both GitHub and local: {local_error}"
                )
    
    @classmethod
    def process_secret(cls, secret_cipher: list) -> str:
        """Process encrypted secret to base32 format.
        
        Args:
            secret_cipher: Encrypted secret bytes
            
        Returns:
            Base32-encoded secret string
        """
        processed = [byte ^ ((i % 33) + 9) for i, byte in enumerate(secret_cipher)]
        processed_str = "".join(map(str, processed))
        utf8_bytes = processed_str.encode('utf-8')
        hex_str = utf8_bytes.hex()
        secret_bytes = bytes.fromhex(hex_str)
        return base64.b32encode(secret_bytes).decode('utf-8')
    
    @classmethod
    def get_server_time(cls, timeout: int = 10) -> int:
        """Get Spotify server time.
        
        Args:
            timeout: Request timeout in seconds
            
        Returns:
            Server timestamp in milliseconds
            
        Raises:
            SpotifyAuthError: If server time cannot be fetched
        """
        headers = {
            "Host": "open.spotify.com",
            "User-Agent": get_random_user_agent(),
            "Accept": "*/*",
        }
        
        try:
            resp = requests.get(
                "https://open.spotify.com/api/server-time",
                headers=headers,
                timeout=timeout
            )
            if resp.status_code != 200:
                raise SpotifyAuthError(
                    f"Failed to get server time. Status code: {resp.status_code}"
                )
            
            data = resp.json()
            server_time = data.get("serverTime")
            
            if server_time is None:
                raise SpotifyAuthError("Failed to fetch server time from Spotify")
            
            return server_time
            
        except SpotifyAuthError:
            raise
        except Exception as e:
            raise SpotifyAuthError(f"Error getting server time: {e}")
    
    @classmethod
    def generate_totp(cls, timeout: int = 10) -> Tuple[pyotp.TOTP, int, int]:
        """Generate TOTP token for Spotify API.
        
        Args:
            timeout: Request timeout in seconds
            
        Returns:
            Tuple of (totp_instance, server_time, secret_version)
            
        Raises:
            SpotifyAuthError: If TOTP generation fails
            
        Example:
            >>> totp, server_time, version = SpotifySecretManager.generate_totp()
            >>> token = totp.at(server_time // 1000)
        """
        # Fetch secrets
        secrets_list, used_local = cls.fetch_secrets(timeout)
        
        # Get latest secret
        try:
            latest_entry = max(secrets_list, key=lambda x: x["version"])
            version = latest_entry["version"]
            secret_cipher = latest_entry["secret"]
        except Exception as e:
            raise SpotifyAuthError(f"Failed to process secrets: {e}")
        
        # Process secret and create TOTP
        b32_secret = cls.process_secret(secret_cipher)
        totp = pyotp.TOTP(b32_secret)
        
        # Get server time
        server_time = cls.get_server_time(timeout)
        
        return totp, server_time, version


__all__ = [
    "SpotifySecretManager",
    "SpotifyAuthError",
]
