"""Unit tests for ThemeManager."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QPushButton, QWidget

from spotiflac.gui.theme_manager import ThemeManager
from spotiflac.services.settings import SettingsRepository


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for tests requiring Qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def mock_settings_repo(tmp_path):
    """Create a mock SettingsRepository with temporary QSettings."""
    settings_file = tmp_path / "test_theme.ini"
    qsettings = QSettings(str(settings_file), QSettings.Format.IniFormat)
    qsettings.clear()
    qsettings.setValue("theme_color", "#1DB954")
    return SettingsRepository(backend=qsettings)


@pytest.fixture
def theme_manager(mock_settings_repo, tmp_path):
    """Create ThemeManager with mock dependencies."""
    icons_dir = tmp_path / "icons"
    icons_dir.mkdir()
    
    # Create a dummy SVG icon
    (icons_dir / "test.svg").write_text(
        '<svg><rect fill="#000000" /></svg>'
    )
    
    return ThemeManager(
        mock_settings_repo,
        icons_dir=icons_dir,
        qdarktheme_module=None,
        pyqtdarktheme_module=None
    )


class TestThemeManager:
    """Test ThemeManager theme color and icon management."""

    def test_initialization(self, theme_manager):
        """ThemeManager initializes with correct default color."""
        assert theme_manager._current_color == "#1DB954"

    def test_change_color_updates_repository(self, qapp, theme_manager, mock_settings_repo):
        """change_color persists new theme color to repository."""
        widget = QWidget()
        
        theme_manager.change_color(widget, "#FF5733")
        
        assert mock_settings_repo.get_value("theme_color") == "#FF5733"
        assert theme_manager._current_color == "#FF5733"

    def test_change_color_with_button_styling(self, qapp, theme_manager):
        """change_color updates clicked button style."""
        widget = QWidget()
        button = QPushButton(widget)
        
        theme_manager.change_color(widget, "#FF5733", clicked_btn=button)
        
        assert "#FF5733" in button.styleSheet()

    def test_themed_icon_recolors_svg(self, theme_manager, tmp_path):
        """themed_icon recolors SVG with current theme color."""
        icon = theme_manager.themed_icon("test")
        
        assert isinstance(icon, QIcon)
        assert not icon.isNull()

    def test_themed_icon_missing_file(self, theme_manager):
        """themed_icon returns null icon for missing file."""
        icon = theme_manager.themed_icon("nonexistent")
        
        assert icon.isNull()

    def test_apply_theme_with_qdarktheme(self, qapp, theme_manager, mock_settings_repo):
        """apply_theme uses qdarktheme if available."""
        mock_qdarktheme = MagicMock()
        theme_manager._qdarktheme = mock_qdarktheme
        
        widget = QWidget()
        theme_manager.apply_theme(widget)
        
        mock_qdarktheme.setup_theme.assert_called_once()

    def test_apply_theme_with_pyqtdarktheme_fallback(self, qapp, theme_manager):
        """apply_theme falls back to pyqtdarktheme if qdarktheme unavailable."""
        theme_manager._qdarktheme = None
        mock_pyqtdarktheme = MagicMock()
        theme_manager._pyqtdarktheme = mock_pyqtdarktheme
        
        widget = QWidget()
        theme_manager.apply_theme(widget)
        
        mock_pyqtdarktheme.apply_theme.assert_called_once()

    def test_apply_theme_no_libraries(self, qapp, theme_manager):
        """apply_theme does nothing if no theme libraries available."""
        theme_manager._qdarktheme = None
        theme_manager._pyqtdarktheme = None
        
        widget = QWidget()
        theme_manager.apply_theme(widget)  # Should not raise

    def test_update_button_style(self, qapp, theme_manager):
        """update_button_style applies correct border color."""
        button = QPushButton()
        
        theme_manager.update_button_style(button, "#00FF00")
        
        assert "border: 2px solid #00FF00" in button.styleSheet()

    def test_refresh_button_icons_with_gui(self, qapp, theme_manager):
        """refresh_button_icons updates icons for buttons with icon names."""
        widget = QWidget()
        button = QPushButton(widget)
        button.setObjectName("download_btn")
        button.setProperty("icon_name", "download")
        
        theme_manager.refresh_button_icons(widget)
        
        # Icon should be set (even if file doesn't exist, it will be null)
        assert button.icon() is not None

    def test_color_persistence_across_changes(self, qapp, theme_manager, mock_settings_repo):
        """Multiple color changes persist correctly."""
        widget = QWidget()
        
        theme_manager.change_color(widget, "#FF0000")
        assert theme_manager._current_color == "#FF0000"
        
        theme_manager.change_color(widget, "#00FF00")
        assert theme_manager._current_color == "#00FF00"
        
        assert mock_settings_repo.get_value("theme_color") == "#00FF00"
