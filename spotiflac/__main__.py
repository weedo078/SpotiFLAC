"""CLI entry point for SpotiFLAC application.

Usage:
    python -m spotiflac.app
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication
from SpotiFLAC import SpotiFLACGUI


def main() -> int:
    """Launch the SpotiFLAC GUI application."""
    app = QApplication(sys.argv)
    window = SpotiFLACGUI()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
