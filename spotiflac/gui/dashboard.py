from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QAbstractItemView,
    QLineEdit,
    QPushButton,
)


class DashboardTab:
    """Encapsulates construction of the dashboard UI."""

    def __init__(self, owner) -> None:
        self.owner = owner
        self.widget = QWidget()
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout()
        self._setup_info_widget(layout)
        self._setup_track_list(layout)
        self._setup_track_buttons(layout)
        self.widget.setLayout(layout)

    def _setup_info_widget(self, layout: QVBoxLayout) -> None:
        owner = self.owner
        owner.info_widget = QWidget()
        info_layout = QHBoxLayout()

        owner.cover_label = QLabel()
        owner.cover_label.setFixedSize(80, 80)
        owner.cover_label.setScaledContents(True)
        info_layout.addWidget(owner.cover_label)

        text_info_layout = QVBoxLayout()
        owner.title_label = QLabel()
        owner.title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        owner.title_label.setWordWrap(True)

        owner.artists_label = QLabel()
        owner.artists_label.setWordWrap(True)

        owner.followers_label = QLabel()
        owner.followers_label.setWordWrap(True)

        owner.release_date_label = QLabel()
        owner.release_date_label.setWordWrap(True)

        owner.type_label = QLabel()
        owner.type_label.setStyleSheet("font-size: 12px;")

        text_info_layout.addWidget(owner.title_label)
        text_info_layout.addWidget(owner.artists_label)
        text_info_layout.addWidget(owner.followers_label)
        text_info_layout.addWidget(owner.release_date_label)
        text_info_layout.addWidget(owner.type_label)
        text_info_layout.addStretch()

        info_layout.addLayout(text_info_layout, 1)

        self._setup_search_widget(info_layout)

        owner.info_widget.setLayout(info_layout)
        owner.info_widget.setFixedHeight(100)
        owner.info_widget.hide()
        layout.addWidget(owner.info_widget)

    def _setup_search_widget(self, info_layout: QHBoxLayout) -> None:
        owner = self.owner
        owner.search_widget = QWidget()
        search_layout = QVBoxLayout()
        search_layout.setContentsMargins(10, 0, 0, 0)
        search_layout.addStretch()

        search_input_layout = QHBoxLayout()
        search_input_layout.addStretch()

        owner.search_input = QLineEdit()
        owner.search_input.setPlaceholderText("Search...")
        owner.search_input.setClearButtonEnabled(True)
        owner.search_input.textChanged.connect(owner.filter_tracks)
        owner.search_input.setFixedWidth(250)

        search_input_layout.addWidget(owner.search_input)
        search_layout.addLayout(search_input_layout)

        owner.search_widget.setLayout(search_layout)
        owner.search_widget.hide()
        info_layout.addWidget(owner.search_widget)

    def _setup_track_list(self, layout: QVBoxLayout) -> None:
        owner = self.owner
        owner.track_list = QListWidget()
        owner.track_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        layout.addWidget(owner.track_list)

    def _setup_track_buttons(self, layout: QVBoxLayout) -> None:
        owner = self.owner
        owner.btn_layout = QHBoxLayout()
        owner.download_btn = QPushButton(' Download')
        owner.delete_btn = QPushButton(' Delete')
        owner.delete_btn.setIcon(owner.get_themed_icon('trash.svg'))

        for btn in [owner.download_btn, owner.delete_btn]:
            btn.setFixedWidth(120)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        owner.download_btn.clicked.connect(owner.download_tracks_action)
        owner.delete_btn.clicked.connect(owner.delete_tracks)

        owner.btn_layout.addStretch()
        owner.btn_layout.addWidget(owner.download_btn)
        owner.btn_layout.addWidget(owner.delete_btn)
        owner.btn_layout.addStretch()

        owner.single_track_container = QWidget()
        single_track_layout = QHBoxLayout(owner.single_track_container)
        single_track_layout.setContentsMargins(0, 0, 0, 0)

        owner.single_download_btn = QPushButton(' Download')
        owner.single_delete_btn = QPushButton(' Delete')
        owner.single_delete_btn.setIcon(owner.get_themed_icon('trash.svg'))

        for btn in [owner.single_download_btn, owner.single_delete_btn]:
            btn.setFixedWidth(120)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        owner.single_download_btn.clicked.connect(owner.download_tracks_action)
        owner.single_delete_btn.clicked.connect(owner.delete_tracks)

        single_track_layout.addStretch()
        single_track_layout.addWidget(owner.single_download_btn)
        single_track_layout.addWidget(owner.single_delete_btn)
        single_track_layout.addStretch()
        owner.single_track_container.hide()

        layout.addLayout(owner.btn_layout)
        layout.addWidget(owner.single_track_container)
