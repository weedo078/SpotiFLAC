from __future__ import annotations

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel


class AboutTab:
    """Simple About tab mirroring the legacy UI layout."""

    def __init__(self, owner) -> None:
        self.owner = owner
        self.widget = QWidget()
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        sections = [
            ("Check for Updates", "Check", "https://github.com/afkarxyz/SpotiFLAC/releases"),
            ("Report an Issue", "Report", "https://github.com/afkarxyz/SpotiFLAC/issues"),
        ]

        for title, button_text, url in sections:
            section_widget = QWidget()
            section_layout = QVBoxLayout(section_widget)
            section_layout.setSpacing(10)
            section_layout.setContentsMargins(0, 0, 0, 0)

            label = QLabel(title)
            label.setStyleSheet("color: palette(text); font-weight: bold;")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            section_layout.addWidget(label)

            button = QPushButton(button_text)
            button.setFixedSize(120, 25)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _, target=url: self._open_url(target))
            section_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)

            layout.addWidget(section_widget)

        footer_label = QLabel(f"v{self.owner.current_version} | October 2025")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer_label)

        self.widget.setLayout(layout)

    @staticmethod
    def _open_url(url: str) -> None:
        normalized = url if url.startswith(("http://", "https://")) else f"https://{url}"
        QDesktopServices.openUrl(QUrl(normalized))
