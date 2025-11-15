from __future__ import annotations

from typing import Any, Optional

from PyQt6.QtWidgets import QApplication


def apply_qdarktheme_primary_color(qdarktheme_module: Optional[Any], color: str) -> bool:
    """Apply primary color using qdarktheme if available."""

    if not qdarktheme_module or not hasattr(qdarktheme_module, "setup_theme"):
        return False

    qdarktheme_module.setup_theme(custom_colors={"[dark]": {"primary": color}})
    return True


def apply_pyqtdarktheme_palette(pyqtdarktheme_module: Optional[Any], app: QApplication, color: str) -> bool:
    """Fallback theming using pyqtdarktheme if qdarktheme is missing."""

    if not pyqtdarktheme_module:
        return False

    palette = pyqtdarktheme_module.load_palette("dark")
    app.setPalette(palette)
    stylesheet = pyqtdarktheme_module.load_stylesheet("dark")
    if color and isinstance(color, str):
        stylesheet = stylesheet.replace("#2196F3", color)
    app.setStyleSheet(stylesheet)
    return True


def get_available_theme_modules() -> dict[str, bool]:
    """Helper mainly for diagnostics/tests."""

    availability = {"qdarktheme": False, "pyqtdarktheme": False}
    try:
        import qdarktheme  # type: ignore  # pragma: no cover

        availability["qdarktheme"] = True
    except Exception:  # pragma: no cover - optional dependency
        pass

    try:
        import pyqtdarktheme  # type: ignore  # pragma: no cover

        availability["pyqtdarktheme"] = True
    except Exception:  # pragma: no cover - optional dependency
        pass

    return availability


__all__ = [
    "apply_qdarktheme_primary_color",
    "apply_pyqtdarktheme_palette",
    "get_available_theme_modules",
]
