"""Service layer facades for networking, settings, and theming."""

from .spotify import SpotifyMetadataService, SpotifyInvalidUrlException
from .tidal import (
    create_tidal_downloader,
    get_available_tidal_apis,
    check_tidal_status,
)
from .deezer import create_deezer_downloader, check_deezer_status
from .settings import AppSettings, SettingsRepository, SettingsService
from .theming import (
    apply_qdarktheme_primary_color,
    apply_pyqtdarktheme_palette,
    get_available_theme_modules,
)

__all__ = [
    "SpotifyMetadataService",
    "SpotifyInvalidUrlException",
    "create_tidal_downloader",
    "get_available_tidal_apis",
    "check_tidal_status",
    "create_deezer_downloader",
    "check_deezer_status",
    "SettingsService",
    "SettingsRepository",
    "AppSettings",
    "apply_qdarktheme_primary_color",
    "apply_pyqtdarktheme_palette",
    "get_available_theme_modules",
]
