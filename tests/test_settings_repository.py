"""Unit tests for SettingsRepository and AppSettings."""
from __future__ import annotations

import pytest
from PyQt6.QtCore import QSettings

from spotiflac.services.settings import AppSettings, SettingsRepository


@pytest.fixture
def mock_qsettings(tmp_path):
    """Create a temporary QSettings instance for testing."""
    settings_file = tmp_path / "test_settings.ini"
    settings = QSettings(str(settings_file), QSettings.Format.IniFormat)
    settings.clear()
    return settings


@pytest.fixture
def settings_repo(mock_qsettings):
    """Create a SettingsRepository with mock QSettings."""
    return SettingsRepository(backend=mock_qsettings)


class TestAppSettings:
    """Test AppSettings dataclass defaults and behavior."""

    def test_default_values(self):
        """Verify all default values are set correctly."""
        settings = AppSettings()
        
        assert settings.output_path == ""
        assert settings.spotify_url == ""
        assert settings.service == "deezer"
        assert settings.tidal_api == "auto"
        assert settings.filename_format == "title_artist"
        assert settings.use_track_numbers is True
        assert settings.use_artist_subfolders is False
        assert settings.use_album_subfolders is True
        assert settings.deezer_fallback is True
        assert settings.track_list_format == "track_artist_date_duration"
        assert settings.date_format == "yyyy"
        assert settings.theme_color == "#1DB954"


class TestSettingsRepository:
    """Test SettingsRepository facade for typed settings access."""

    def test_load_with_defaults(self, settings_repo):
        """Loading settings without persisted values returns defaults."""
        app_settings = settings_repo.load()
        
        assert isinstance(app_settings, AppSettings)
        assert app_settings.service == "deezer"
        assert app_settings.theme_color == "#1DB954"

    def test_load_with_existing_values(self, mock_qsettings, settings_repo):
        """Loading settings with persisted values returns those values."""
        mock_qsettings.setValue("service", "tidal")
        mock_qsettings.setValue("theme_color", "#FF5733")
        mock_qsettings.setValue("use_track_numbers", False)
        
        app_settings = settings_repo.load()
        
        assert app_settings.service == "tidal"
        assert app_settings.theme_color == "#FF5733"
        assert app_settings.use_track_numbers is False

    def test_get_value(self, mock_qsettings, settings_repo):
        """get_value returns persisted value or default."""
        mock_qsettings.setValue("service", "tidal")
        
        assert settings_repo.get_value("service") == "tidal"
        assert settings_repo.get_value("filename_format") == "title_artist"

    def test_update_values_single(self, settings_repo, mock_qsettings):
        """update_values persists a single setting."""
        settings_repo.update_values(service="tidal")
        
        assert mock_qsettings.value("service") == "tidal"

    def test_update_values_multiple(self, settings_repo, mock_qsettings):
        """update_values persists multiple settings atomically."""
        settings_repo.update_values(
            service="tidal",
            theme_color="#00FF00",
            use_track_numbers=False
        )
        
        assert mock_qsettings.value("service") == "tidal"
        assert mock_qsettings.value("theme_color") == "#00FF00"
        assert mock_qsettings.value("use_track_numbers") == "false"

    def test_update_values_empty(self, settings_repo):
        """update_values with no arguments does nothing."""
        settings_repo.update_values()  # Should not raise

    def test_type_coercion_bool(self, mock_qsettings, settings_repo):
        """Boolean values are correctly coerced from QSettings strings."""
        mock_qsettings.setValue("use_track_numbers", "true")
        
        app_settings = settings_repo.load()
        assert app_settings.use_track_numbers is True
        
        mock_qsettings.setValue("use_track_numbers", "false")
        app_settings = settings_repo.load()
        assert app_settings.use_track_numbers is False

    def test_unknown_field_ignored(self, mock_qsettings, settings_repo):
        """Unknown fields in QSettings are ignored during load."""
        mock_qsettings.setValue("unknown_field", "some_value")
        
        app_settings = settings_repo.load()
        assert not hasattr(app_settings, "unknown_field")

    def test_sync_called_after_update(self, settings_repo, mock_qsettings, mocker):
        """Verify sync is called after update_values."""
        spy = mocker.spy(mock_qsettings, "sync")
        
        settings_repo.update_values(service="tidal")
        
        spy.assert_called_once()
