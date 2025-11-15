from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Type

from PyQt6.QtCore import QSettings


class SettingsService:
    """Thin wrapper around :class:`QSettings` for easier swapping/testing."""

    def __init__(
        self,
        organization: str = "SpotiFLAC",
        application: str = "Settings",
        *,
        backend: Optional[QSettings] = None,
    ) -> None:
        self._settings = backend or QSettings(organization, application)

    @property
    def backend(self) -> QSettings:
        return self._settings

    def get(self, key: str, default: Any = None, *, data_type: Optional[Type[Any]] = None) -> Any:
        if data_type is not None:
            return self._settings.value(key, default, type=data_type)
        return self._settings.value(key, default)

    def set(self, key: str, value: Any) -> None:
        self._settings.setValue(key, value)

    def sync(self) -> None:
        self._settings.sync()


@dataclass(frozen=True)
class SettingField:
    key: str
    default: Any
    data_type: Optional[Type[Any]] = None


@dataclass
class AppSettings:
    output_path: str = str(Path.home() / "Music")
    spotify_url: str = ""
    filename_format: str = "title_artist"
    use_track_numbers: bool = False
    use_artist_subfolders: bool = False
    use_album_subfolders: bool = False
    service: str = "tidal"
    tidal_api: str = "auto"
    deezer_fallback: bool = True
    check_for_updates: bool = True
    theme_color: str = "#2196F3"
    track_list_format: str = "track_artist_date_duration"
    date_format: str = "dd_mm_yyyy"


_SETTINGS_FIELDS: Dict[str, SettingField] = {
    "output_path": SettingField("output_path", AppSettings.output_path),
    "spotify_url": SettingField("spotify_url", AppSettings.spotify_url),
    "filename_format": SettingField("filename_format", AppSettings.filename_format),
    "use_track_numbers": SettingField("use_track_numbers", AppSettings.use_track_numbers, bool),
    "use_artist_subfolders": SettingField(
        "use_artist_subfolders", AppSettings.use_artist_subfolders, bool
    ),
    "use_album_subfolders": SettingField(
        "use_album_subfolders", AppSettings.use_album_subfolders, bool
    ),
    "service": SettingField("service", AppSettings.service),
    "tidal_api": SettingField("tidal_api", AppSettings.tidal_api),
    "deezer_fallback": SettingField("deezer_fallback", AppSettings.deezer_fallback, bool),
    "check_for_updates": SettingField("check_for_updates", AppSettings.check_for_updates, bool),
    "theme_color": SettingField("theme_color", AppSettings.theme_color),
    "track_list_format": SettingField(
        "track_list_format", AppSettings.track_list_format
    ),
    "date_format": SettingField("date_format", AppSettings.date_format),
}


class SettingsRepository:
    """Typed façade that exposes application settings with defaults."""

    def __init__(self, service: Optional[SettingsService] = None) -> None:
        self._service = service or SettingsService()

    def load(self) -> AppSettings:
        data: Dict[str, Any] = {}
        for attr, field in _SETTINGS_FIELDS.items():
            data[attr] = self._service.get(field.key, field.default, data_type=field.data_type)
        return AppSettings(**data)

    def get_value(self, attr: str) -> Any:
        field = self._get_field(attr)
        return self._service.get(field.key, field.default, data_type=field.data_type)

    def update_values(self, **kwargs: Any) -> None:
        if not kwargs:
            return
        for attr, value in kwargs.items():
            field = self._get_field(attr)
            self._service.set(field.key, value)
        self._service.sync()

    def backend(self) -> QSettings:
        return self._service.backend

    @staticmethod
    def _get_field(attr: str) -> SettingField:
        if attr not in _SETTINGS_FIELDS:
            raise KeyError(f"Unknown settings attribute '{attr}'")
        return _SETTINGS_FIELDS[attr]


__all__ = ["SettingsService", "SettingsRepository", "AppSettings", "SettingField"]
