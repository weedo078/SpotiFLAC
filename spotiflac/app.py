"""SpotiFLAC GUI Application Entry Point.

This module provides the main entry point for the SpotiFLAC GUI application.
It can be run directly or imported and used programmatically.

Usage:
    # Run directly
    python -m spotiflac.app
    
    # Or import
    from spotiflac.app import main
    main()
"""
from __future__ import annotations

import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

# Import GUI components
from spotiflac.gui import (
    DashboardTab,
    ProcessTab,
    SettingsTab,
    ThemeTab,
    AboutTab
)
from spotiflac.controllers import DownloadController
from spotiflac.services import SettingsRepository
from spotiflac.gui.theme_manager import ThemeManager
from spotiflac.utils import setup_logging


class SpotiFLACApp(QApplication):
    """Main SpotiFLAC Application.
    
    Extends QApplication to provide application-wide setup and configuration.
    """
    
    def __init__(self, argv: list[str]):
        """Initialize application.
        
        Args:
            argv: Command line arguments
        """
        super().__init__(argv)
        
        # Setup logging
        self._setup_logging()
        
        # Set application metadata
        self.setApplicationName("SpotiFLAC")
        self.setApplicationDisplayName("SpotiFLAC")
        self.setOrganizationName("SpotiFLAC")
        self.setOrganizationDomain("spotiflac.local")
        
        # Set application icon
        self._setup_icon()
        
        # Initialize services
        self.settings = SettingsRepository()
        self.theme_manager = ThemeManager(self.settings)
        
        # Apply theme
        self._apply_theme()
        
        # Create main window (import the monolithic GUI for now)
        # TODO: This should be refactored into a proper MainWindow class
        # For now, we import the legacy SpotiFLACGUI class
        import SpotiFLAC as legacy_gui
        self.main_window = legacy_gui.SpotiFLACGUI()
        
        # Override the main window's settings and theme manager
        self.main_window.settings_repo = self.settings
        self.main_window.theme_manager = self.theme_manager
    
    def _setup_logging(self) -> None:
        """Setup application logging."""
        # Change to DEBUG for detailed output
        log_level = logging.DEBUG
        log_file = Path.home() / ".spotiflac" / "spotiflac.log"
        
        setup_logging(
            level=log_level,
            log_file=log_file,
            console=True
        )
        
        logger = logging.getLogger(__name__)
        logger.info("SpotiFLAC application starting...")
    
    def _setup_icon(self) -> None:
        """Setup application icon."""
        icon_path = Path(__file__).parent.parent / "icons" / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
    
    def _apply_theme(self) -> None:
        """Apply saved theme settings."""
        try:
            settings = self.settings.load()
            theme_color = settings.theme_color
            
            if theme_color:
                self.theme_manager.apply_theme(theme_color)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to apply theme: {e}")
    
    def run(self) -> int:
        """Run the application.
        
        Returns:
            Exit code
        """
        self.main_window.show()
        return self.exec()


def main(argv: list[str] = None) -> int:
    """Main entry point for SpotiFLAC GUI.
    
    Args:
        argv: Optional command line arguments (defaults to sys.argv)
        
    Returns:
        Exit code
        
    Example:
        >>> from spotiflac.app import main
        >>> sys.exit(main())
    """
    if argv is None:
        argv = sys.argv
    
    app = SpotiFLACApp(argv)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
