from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Sequence, Tuple

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QApplication, QPushButton

from spotiflac.services import (
    SettingsRepository,
    apply_pyqtdarktheme_palette,
    apply_qdarktheme_primary_color,
)

LOGGER = logging.getLogger(__name__)


class ThemeManager:
    """Centralizes theme color changes and icon recoloring."""

    _ICON_MAPPING: Sequence[Tuple[str, str]] = (
        ("download_btn", "download.svg"),
        ("delete_btn", "trash.svg"),
        ("single_download_btn", "download.svg"),
        ("single_delete_btn", "trash.svg"),
        ("fix_error_btn", "tool.svg"),
        ("remove_successful_btn", "circle-x.svg"),
    )

    def __init__(
        self,
        settings_repo: SettingsRepository,
        *,
        icons_dir: Optional[Path] = None,
        qdarktheme_module: Optional[object] = None,
        pyqtdarktheme_module: Optional[object] = None,
    ) -> None:
        self._settings_repo = settings_repo
        self._icons_dir = Path(icons_dir) if icons_dir else Path(__file__).resolve().parents[2] / "icons"
        self._qdarktheme = qdarktheme_module or self._import_optional_module("qdarktheme")
        self._pyqtdarktheme = pyqtdarktheme_module or self._import_optional_module("pyqtdarktheme")
        self._current_color = str(self._settings_repo.get_value("theme_color"))

    @staticmethod
    def _import_optional_module(name: str) -> Optional[object]:
        try:
            return __import__(name)
        except Exception:  # pragma: no cover - optional dependency
            return None

    @property
    def current_color(self) -> str:
        return self._current_color

    def apply_theme(self, app: Optional[QApplication]) -> None:
        self._apply_theme_color(app, self._current_color)

    def set_color(self, color: str, *, app: Optional[QApplication] = None) -> None:
        if color == self._current_color:
            return
        self._current_color = color
        self._settings_repo.update_values(theme_color=color)
        self._apply_theme_color(app or QApplication.instance(), color)

    def change_color(
        self,
        owner: object,
        color: str,
        clicked_btn: Optional[QPushButton] = None,
    ) -> None:
        previous_color = getattr(owner, "current_theme_color", self._current_color)
        self._reset_button_style(owner, previous_color)
        self.set_color(color)
        owner.current_theme_color = color
        if clicked_btn is not None:
            clicked_btn.setStyleSheet(self._button_stylesheet(color, selected=True))
        self.refresh_button_icons(owner)

    def refresh_button_icons(self, owner: object) -> None:
        for attr_name, icon_name in self._ICON_MAPPING:
            button = getattr(owner, attr_name, None)
            if button is not None:
                button.setIcon(self.themed_icon(icon_name))

    def themed_icon(
        self,
        icon_name: str,
        *,
        size: Optional[Tuple[int, int]] = None,
    ) -> QIcon:
        icon_path = self._icons_dir / icon_name
        if not icon_path.exists():
            LOGGER.warning("Icon %s not found in %s", icon_name, self._icons_dir)
            return QIcon()

        data = icon_path.read_text(encoding="utf-8")
        svg_content = data.replace("currentColor", self._current_color)

        icon_size = QSize(*(size or (16, 16)))
        renderer = QSvgRenderer(svg_content.encode("utf-8"))
        pixmap = QPixmap(icon_size)
        pixmap.fill(QColor(0, 0, 0, 0))

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _apply_theme_color(self, app: Optional[QApplication], color: str) -> None:
        applied = apply_qdarktheme_primary_color(self._qdarktheme, color)
        if applied or not app:
            return
        fallback_applied = apply_pyqtdarktheme_palette(self._pyqtdarktheme, app, color)
        if not fallback_applied:
            LOGGER.warning("Kein Dark-Theme-Modul verfügbar – UI wird ohne Theme gestartet.")

    def _reset_button_style(self, owner: object, color: str) -> None:
        color_buttons = getattr(owner, "color_buttons", {})
        button = color_buttons.get(color)
        if button is not None:
            button.setStyleSheet(self._button_stylesheet(color, selected=False))

    @staticmethod
    def _button_stylesheet(color: str, *, selected: bool) -> str:
        border = "2px solid #fff" if selected else "none"
        return (
            f"QPushButton {{ background-color: {color}; border: {border}; border-radius: 9px; }}"
            "QPushButton:hover { border: 2px solid #fff; }"
            "QPushButton:pressed { border: 2px solid #fff; }"
        )


__all__ = ["ThemeManager"]
