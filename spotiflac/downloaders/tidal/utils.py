"""Utility functions for Tidal downloader."""
from __future__ import annotations

from typing import List, Dict, Any, Optional
import requests
import json

from spotiflac.downloaders import DownloadError


class TidalAPIDiscoveryError(DownloadError):
    """Raised when API discovery fails."""
    pass


class TidalAPIDiscovery:
    """Discover and manage Tidal API instances.
    
    Fetches available API instances from status server and provides
    methods to select the best performing instance.
    
    Example:
        >>> discovery = TidalAPIDiscovery()
        >>> apis = discovery.get_available_apis()
        >>> best = discovery.get_best_api()
    """
    
    STATUS_URL = "https://status.monochrome.tf/api/stream"
    
    @classmethod
    def get_available_apis(
        cls,
        *,
        timeout: int = 10,
        only_successful: bool = True,
    ) -> List[Dict[str, Any]]:
        """Fetch list of available Tidal API instances.
        
        Uses Server-Sent Events (SSE) stream to get real-time status.
        
        Args:
            timeout: Request timeout in seconds
            only_successful: Only return instances that are online
            
        Returns:
            List of API instances sorted by response time
            
        Example:
            >>> apis = TidalAPIDiscovery.get_available_apis()
            >>> for api in apis:
            ...     print(api['url'], api['uptime'])
        """
        try:
            response = requests.get(
                cls.STATUS_URL,
                timeout=timeout,
                stream=True
            )
            response.raise_for_status()
            
            # Parse SSE stream
            for line in response.iter_lines():
                if not line:
                    continue
                
                line_str = line.decode('utf-8')
                
                # SSE format: "data: {json}"
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        
                        # Extract API instances
                        instances = data.get('instances', [])
                        
                        # Filter for API instances
                        api_instances = [
                            inst for inst in instances
                            if inst.get('instance_type') == 'api'
                        ]
                        
                        # Filter for successful instances if requested
                        if only_successful:
                            api_instances = [
                                inst for inst in api_instances
                                if inst.get('last_check', {}).get('success')
                            ]
                        
                        # Sort by average response time
                        api_instances.sort(
                            key=lambda x: x.get('avg_response_time', 9999)
                        )
                        
                        return api_instances
                        
                    except json.JSONDecodeError:
                        continue
            
            return []
            
        except requests.exceptions.RequestException as e:
            raise TidalAPIDiscoveryError(f"Failed to fetch API list: {e}")
    
    @classmethod
    def get_best_api(cls, **kwargs) -> Optional[str]:
        """Get URL of best performing API instance.
        
        Args:
            **kwargs: Passed to get_available_apis()
            
        Returns:
            URL of best API, or None if none available
        """
        apis = cls.get_available_apis(**kwargs)
        return apis[0]['url'] if apis else None
    
    @classmethod
    def get_api_with_fallback(
        cls,
        preferred_url: Optional[str] = None,
        **kwargs
    ) -> str:
        """Get API URL with automatic fallback.
        
        Args:
            preferred_url: Preferred API URL (e.g., "auto" or specific URL)
            **kwargs: Passed to get_available_apis()
            
        Returns:
            API URL to use
            
        Raises:
            TidalAPIDiscoveryError: If no API available
        """
        # If preferred URL is "auto" or None, discover best
        if not preferred_url or preferred_url == "auto":
            best = cls.get_best_api(**kwargs)
            if not best:
                raise TidalAPIDiscoveryError("No Tidal API instances available")
            return best
        
        # Use preferred URL
        return preferred_url


__all__ = [
    "TidalAPIDiscovery",
    "TidalAPIDiscoveryError",
]
