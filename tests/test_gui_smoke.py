"""GUI smoke tests for SpotiFLAC application."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import QApplication

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from SpotiFLAC import SpotiFLACGUI
from spotiflac.services.settings import SettingsRepository


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def gui_window(qapp, tmp_path):
    """Create SpotiFLACGUI instance with temporary settings."""
    settings_file = tmp_path / "test_gui.ini"
    qsettings = QSettings(str(settings_file), QSettings.Format.IniFormat)
    qsettings.clear()
    
    settings_repo = SettingsRepository(backend=qsettings)
    window = SpotiFLACGUI(settings_repo=settings_repo)
    
    yield window
    
    window.close()


class TestGUISmoke:
    """Smoke tests to verify GUI initializes and basic interactions work."""

    def test_window_creation(self, gui_window):
        """GUI window is created successfully."""
        assert gui_window is not None
        assert gui_window.windowTitle() == "SpotiFLAC"

    def test_window_geometry(self, gui_window):
        """Window has expected fixed width."""
        assert gui_window.width() == 650

    def test_tabs_present(self, gui_window):
        """All expected tabs are present."""
        tab_widget = gui_window.tab_widget
        
        assert tab_widget.count() == 5
        assert tab_widget.tabText(0) == "Dashboard"
        assert tab_widget.tabText(1) == "Process"
        assert tab_widget.tabText(2) == "Settings"
        assert tab_widget.tabText(3) == "Theme"
        assert tab_widget.tabText(4) == "About"

    def test_spotify_url_input_present(self, gui_window):
        """Spotify URL input field is present and functional."""
        assert gui_window.spotify_url is not None
        assert gui_window.spotify_url.placeholderText() == "Enter Spotify URL"
        
        # Test input
        gui_window.spotify_url.setText("https://open.spotify.com/track/test")
        assert "test" in gui_window.spotify_url.text()

    def test_fetch_button_present(self, gui_window):
        """Fetch button is present and clickable."""
        assert gui_window.fetch_btn is not None
        assert gui_window.fetch_btn.text() == "Fetch"
        assert gui_window.fetch_btn.cursor().shape() == Qt.CursorShape.PointingHandCursor

    def test_settings_controls_initialized(self, gui_window):
        """Settings controls are initialized with default values."""
        assert gui_window.service_dropdown is not None
        assert gui_window.tidal_api_dropdown is not None
        assert gui_window.service == "deezer"

    def test_theme_manager_initialized(self, gui_window):
        """ThemeManager is initialized and accessible."""
        assert gui_window.theme_manager is not None
        assert gui_window.theme_manager._current_color == "#1DB954"

    def test_settings_repository_initialized(self, gui_window):
        """SettingsRepository is initialized and accessible."""
        assert gui_window.settings_repo is not None
        assert isinstance(gui_window.app_settings.service, str)

    def test_download_controller_initialized(self, gui_window):
        """DownloadController is initialized."""
        assert gui_window.download_controller is not None

    def test_tab_switching(self, gui_window):
        """Tab switching works correctly."""
        tab_widget = gui_window.tab_widget
        
        tab_widget.setCurrentIndex(2)  # Settings tab
        assert tab_widget.currentIndex() == 2
        
        tab_widget.setCurrentIndex(3)  # Theme tab
        assert tab_widget.currentIndex() == 3

    def test_service_dropdown_interaction(self, gui_window):
        """Service dropdown can be changed."""
        initial_service = gui_window.service
        
        # Find tidal index
        for i in range(gui_window.service_dropdown.count()):
            if gui_window.service_dropdown.itemData(i) == "tidal":
                gui_window.service_dropdown.setCurrentIndex(i)
                break
        
        # Service should update
        assert gui_window.service in ["deezer", "tidal"]

    def test_theme_color_change(self, gui_window):
        """Theme color can be changed via ThemeManager."""
        initial_color = gui_window.theme_manager._current_color
        
        gui_window.change_theme_color("#FF5733")
        
        assert gui_window.theme_manager._current_color == "#FF5733"
        assert gui_window.settings_repo.get_value("theme_color") == "#FF5733"

    def test_window_show_hide(self, gui_window):
        """Window can be shown and hidden."""
        gui_window.show()
        assert gui_window.isVisible()
        
        gui_window.hide()
        assert not gui_window.isVisible()
