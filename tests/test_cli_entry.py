"""Tests for CLI entry point."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestCLIEntry:
    """Test CLI entry point module."""

    def test_main_function_exists(self):
        """main() function is importable from __main__."""
        from spotiflac.__main__ import main
        
        assert callable(main)

    @patch("spotiflac.__main__.QApplication")
    @patch("spotiflac.__main__.SpotiFLACGUI")
    def test_main_creates_app_and_window(self, mock_gui, mock_qapp):
        """main() creates QApplication and SpotiFLACGUI instances."""
        mock_app_instance = MagicMock()
        mock_qapp.return_value = mock_app_instance
        mock_app_instance.exec.return_value = 0
        
        mock_window = MagicMock()
        mock_gui.return_value = mock_window
        
        from spotiflac.__main__ import main
        
        result = main()
        
        mock_qapp.assert_called_once()
        mock_gui.assert_called_once()
        mock_window.show.assert_called_once()
        mock_app_instance.exec.assert_called_once()
        assert result == 0

    @patch("spotiflac.__main__.QApplication")
    @patch("spotiflac.__main__.SpotiFLACGUI")
    def test_main_returns_exit_code(self, mock_gui, mock_qapp):
        """main() returns QApplication exit code."""
        mock_app_instance = MagicMock()
        mock_qapp.return_value = mock_app_instance
        mock_app_instance.exec.return_value = 42
        
        from spotiflac.__main__ import main
        
        result = main()
        
        assert result == 42

    def test_module_can_be_imported(self):
        """__main__ module can be imported without errors."""
        import spotiflac.__main__
        
        assert hasattr(spotiflac.__main__, "main")
