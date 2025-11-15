from __future__ import annotations

from typing import Any, Optional, Tuple

import requests

# Import new modular downloader
from spotiflac.downloaders.deezer import DeezerDownloader

_STATUS_URL = "https://deezmate.com/"


def create_deezer_downloader(**kwargs: Any):
    """Return a configured DeezerDownloader instance.
    
    Uses new modular downloader.
    """
    return DeezerDownloader(**kwargs)


def check_deezer_status(timeout: float = 5.0) -> Tuple[bool, Optional[str]]:
    """Check availability of the Deezer helper endpoint."""

    try:
        response = requests.get(_STATUS_URL, timeout=timeout)
        response.raise_for_status()
        return True, None
    except Exception as exc:  # pragma: no cover - network dependent
        return False, str(exc)


__all__ = ["create_deezer_downloader", "check_deezer_status"]
