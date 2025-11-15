from __future__ import annotations

from typing import Any, List, Optional, Tuple

import requests

# Import new modular downloader
from spotiflac.downloaders.tidal import TidalDownloader

_STATUS_URL = "https://status.monochrome.tf"


def create_tidal_downloader(*, api_url: Optional[str] = None, **kwargs: Any):
    """Factory to create a configured TidalDownloader.
    
    Uses new modular downloader.
    """
    return TidalDownloader(api_url=api_url, **kwargs)


def get_available_tidal_apis():
    """Expose the downloader's dynamic API discovery."""
    from spotiflac.downloaders.tidal import TidalAPIDiscovery
    return TidalAPIDiscovery.get_available_apis()


def check_tidal_status(timeout: float = 5.0) -> Tuple[bool, Optional[str]]:
    """Ping the public status endpoint used by the GUI indicator."""

    try:
        response = requests.get(_STATUS_URL, timeout=timeout)
        response.raise_for_status()
        return True, None
    except Exception as exc:  # pragma: no cover - purely network related
        return False, str(exc)


__all__ = [
    "create_tidal_downloader",
    "get_available_tidal_apis",
    "check_tidal_status",
]
