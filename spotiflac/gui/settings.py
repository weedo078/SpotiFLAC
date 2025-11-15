from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QCheckBox,
    QRadioButton,
    QButtonGroup,
)


class SettingsTab:
    """Encapsulates the settings tab UI."""

    def __init__(self, owner) -> None:
        self.owner = owner
        self.widget = QWidget()
        self._build()

    def _build(self) -> None:
        owner = self.owner
        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(10, 10, 10, 10)

        self._build_output_section(owner, layout)
        self._build_dashboard_section(owner, layout)
        self._build_file_section(owner, layout)
        self._build_service_section(owner, layout)

        self.widget.setLayout(layout)

    def _build_output_section(self, owner, parent_layout: QVBoxLayout) -> None:
        output_group = QWidget()
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(2)
        output_layout.setContentsMargins(0, 0, 0, 0)

        output_label = QLabel('Output Directory')
        output_label.setStyleSheet("font-weight: bold; margin-top: 0px; margin-bottom: 5px;")
        output_layout.addWidget(output_label)

        output_dir_layout = QHBoxLayout()
        owner.output_dir = QLineEdit()
        owner.output_dir.setText(owner.last_output_path)
        owner.output_dir.textChanged.connect(owner.save_settings)

        owner.output_browse = QPushButton('Browse')
        owner.output_browse.setFixedWidth(80)
        owner.output_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        owner.output_browse.clicked.connect(owner.browse_output)

        output_dir_layout.addWidget(owner.output_dir)
        output_dir_layout.addSpacing(5)
        output_dir_layout.addWidget(owner.output_browse)

        output_layout.addLayout(output_dir_layout)
        parent_layout.addWidget(output_group)

    def _build_dashboard_section(self, owner, parent_layout: QVBoxLayout) -> None:
        dashboard_group = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_group)
        dashboard_layout.setSpacing(3)
        dashboard_layout.setContentsMargins(0, 0, 0, 0)

        dashboard_label = QLabel('Dashboard Settings')
        dashboard_label.setStyleSheet("font-weight: bold; margin-top: 8px; margin-bottom: 5px;")
        dashboard_layout.addWidget(dashboard_label)

        dashboard_controls_layout = QHBoxLayout()
        list_format_label = QLabel('Track List View:')
        list_format_label.setFixedWidth(90)

        owner.track_list_format_dropdown = QComboBox()
        owner.track_list_format_dropdown.addItem("Track - Artist - Date - Duration", "track_artist_date_duration")
        owner.track_list_format_dropdown.addItem("Artist - Track - Date - Duration", "artist_track_date_duration")
        owner.track_list_format_dropdown.addItem("Track - Artist - Date", "track_artist_date")
        owner.track_list_format_dropdown.addItem("Artist - Track - Date", "artist_track_date")
        owner.track_list_format_dropdown.addItem("Track - Artist - Duration", "track_artist_duration")
        owner.track_list_format_dropdown.addItem("Artist - Track - Duration", "artist_track_duration")
        owner.track_list_format_dropdown.addItem("Track - Artist", "track_artist")
        owner.track_list_format_dropdown.addItem("Artist - Track", "artist_track")
        owner.track_list_format_dropdown.currentIndexChanged.connect(owner.save_track_list_format)

        dashboard_controls_layout.addWidget(list_format_label)
        dashboard_controls_layout.addWidget(owner.track_list_format_dropdown)
        dashboard_controls_layout.addSpacing(15)

        date_format_label = QLabel('Date Format:')
        date_format_label.setFixedWidth(80)

        owner.date_format_dropdown = QComboBox()
        owner.date_format_dropdown.addItem("DD-MM-YYYY", "dd_mm_yyyy")
        owner.date_format_dropdown.addItem("YYYY-MM-DD", "yyyy_mm_dd")
        owner.date_format_dropdown.addItem("YYYY", "yyyy")
        owner.date_format_dropdown.currentIndexChanged.connect(owner.save_date_format)

        dashboard_controls_layout.addWidget(date_format_label)
        dashboard_controls_layout.addWidget(owner.date_format_dropdown)
        dashboard_controls_layout.addStretch()

        dashboard_layout.addLayout(dashboard_controls_layout)
        parent_layout.addWidget(dashboard_group)

    def _build_file_section(self, owner, parent_layout: QVBoxLayout) -> None:
        file_group = QWidget()
        file_layout = QVBoxLayout(file_group)
        file_layout.setSpacing(2)
        file_layout.setContentsMargins(0, 0, 0, 0)

        file_label = QLabel('File Settings')
        file_label.setStyleSheet("font-weight: bold; margin-top: 8px; margin-bottom: 5px;")
        file_layout.addWidget(file_label)

        format_layout = QHBoxLayout()
        format_label = QLabel('Filename Format:')
        owner.format_group = QButtonGroup(owner)
        owner.title_artist_radio = QRadioButton('Title - Artist')
        owner.title_artist_radio.setCursor(Qt.CursorShape.PointingHandCursor)
        owner.title_artist_radio.toggled.connect(owner.save_filename_format)

        owner.artist_title_radio = QRadioButton('Artist - Title')
        owner.artist_title_radio.setCursor(Qt.CursorShape.PointingHandCursor)
        owner.artist_title_radio.toggled.connect(owner.save_filename_format)

        owner.title_only_radio = QRadioButton('Title')
        owner.title_only_radio.setCursor(Qt.CursorShape.PointingHandCursor)
        owner.title_only_radio.toggled.connect(owner.save_filename_format)

        if owner.filename_format == "artist_title":
            owner.artist_title_radio.setChecked(True)
        elif owner.filename_format == "title_only":
            owner.title_only_radio.setChecked(True)
        else:
            owner.title_artist_radio.setChecked(True)

        owner.format_group.addButton(owner.title_artist_radio)
        owner.format_group.addButton(owner.artist_title_radio)
        owner.format_group.addButton(owner.title_only_radio)

        format_layout.addWidget(format_label)
        format_layout.addWidget(owner.title_artist_radio)
        format_layout.addSpacing(10)
        format_layout.addWidget(owner.artist_title_radio)
        format_layout.addSpacing(10)
        format_layout.addWidget(owner.title_only_radio)
        format_layout.addStretch()
        file_layout.addLayout(format_layout)

        checkbox_layout = QHBoxLayout()
        owner.artist_subfolder_checkbox = QCheckBox('Artist Subfolder (Playlist)')
        owner.artist_subfolder_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        owner.artist_subfolder_checkbox.setChecked(owner.use_artist_subfolders)
        owner.artist_subfolder_checkbox.toggled.connect(owner.save_artist_subfolder_setting)
        checkbox_layout.addWidget(owner.artist_subfolder_checkbox)
        checkbox_layout.addSpacing(10)

        owner.album_subfolder_checkbox = QCheckBox('Album Subfolder (Playlist)')
        owner.album_subfolder_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        owner.album_subfolder_checkbox.setChecked(owner.use_album_subfolders)
        owner.album_subfolder_checkbox.toggled.connect(owner.save_album_subfolder_setting)
        checkbox_layout.addWidget(owner.album_subfolder_checkbox)
        checkbox_layout.addSpacing(10)

        owner.track_number_checkbox = QCheckBox('Track Number')
        owner.track_number_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        owner.track_number_checkbox.setChecked(owner.use_track_numbers)
        owner.track_number_checkbox.toggled.connect(owner.save_track_numbering)
        checkbox_layout.addWidget(owner.track_number_checkbox)

        checkbox_layout.addStretch()
        file_layout.addLayout(checkbox_layout)
        parent_layout.addWidget(file_group)

    def _build_service_section(self, owner, parent_layout: QVBoxLayout) -> None:
        auth_group = QWidget()
        auth_layout = QVBoxLayout(auth_group)
        auth_layout.setSpacing(2)
        auth_layout.setContentsMargins(0, 0, 0, 0)

        auth_label = QLabel('Service Settings')
        auth_label.setStyleSheet("font-weight: bold; margin-top: 8px; margin-bottom: 5px;")
        auth_layout.addWidget(auth_label)

        service_api_layout = QHBoxLayout()
        service_label = QLabel('Service:')
        service_label.setFixedWidth(53)

        service_api_layout.addWidget(service_label)
        service_api_layout.addWidget(owner.service_dropdown)
        service_api_layout.addSpacing(15)

        owner.tidal_api_label.setFixedWidth(85)
        service_api_layout.addWidget(owner.tidal_api_label)
        service_api_layout.addWidget(owner.tidal_api_dropdown, 1)
        service_api_layout.addSpacing(5)
        service_api_layout.addWidget(owner.refresh_api_btn)
        auth_layout.addLayout(service_api_layout)

        auth_layout.addWidget(owner.tidal_api_hint_label)
        auth_layout.addWidget(owner.deezer_fallback_checkbox)

        parent_layout.addWidget(auth_group)
