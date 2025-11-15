from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from packaging import version

try:
    from mutagen.flac import FLAC
except ImportError:  # pragma: no cover - optional dependency
    FLAC = None

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QLabel, QFileDialog, QTextEdit, QTabWidget, QButtonGroup, QRadioButton,
    QProgressBar, QCheckBox, QDialog,
    QDialogButtonBox, QComboBox, QStyledItemDelegate, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QTimer, QTime, QSize
from PyQt6.QtGui import QIcon, QTextCursor, QDesktopServices, QPixmap, QBrush
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from spotiflac.models import Track
from spotiflac.services import (
    AppSettings,
    SettingsRepository,
    SpotifyInvalidUrlException,
    SpotifyMetadataService,
    check_deezer_status,
    check_tidal_status,
    get_available_tidal_apis,
)
from spotiflac.controllers import DownloadController
from spotiflac.gui import AboutTab, DashboardTab, ProcessTab, SettingsTab, ThemeTab
from spotiflac.gui.theme_manager import ThemeManager

class UpdateDialog(QDialog):
    def __init__(self, current_version, new_version, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Now")
        self.setFixedWidth(400)
        self.setModal(True)

        layout = QVBoxLayout()

        message = QLabel(f"SpotiFLAC v{new_version} Available!")
        message.setWordWrap(True)
        layout.addWidget(message)

        button_box = QDialogButtonBox()
        self.update_button = QPushButton("Check")
        self.update_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button = QPushButton("Later")
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        button_box.addButton(self.update_button, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole)
        
        layout.addWidget(button_box)

        self.setLayout(layout)

        self.update_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

class ServiceStatusDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        item_data = index.data(Qt.ItemDataRole.UserRole)
        is_online = item_data.get('online', False) if item_data else False
        
        super().paint(painter, option, index)
        
        indicator_color = Qt.GlobalColor.green if is_online else Qt.GlobalColor.red
        
        circle_size = 6
        circle_y = option.rect.center().y() - circle_size // 2
        circle_x = option.rect.right() - circle_size - 5
        
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(indicator_color))
        painter.drawEllipse(circle_x, circle_y, circle_size, circle_size)
        painter.restore()

class TidalAPIDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        item_data = index.data(Qt.ItemDataRole.UserRole + 1)
        
        super().paint(painter, option, index)
        
        if item_data and isinstance(item_data, dict) and 'status' in item_data:
            is_online = item_data.get('status') == 'UP'
            indicator_color = Qt.GlobalColor.green if is_online else Qt.GlobalColor.red
            
            circle_size = 6
            circle_y = option.rect.center().y() - circle_size // 2
            circle_x = option.rect.right() - circle_size - 5
            
            painter.save()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(indicator_color))
            painter.drawEllipse(circle_x, circle_y, circle_size, circle_size)
            painter.restore()

class TidalStatusChecker(QThread):
    status_updated = pyqtSignal(bool)
    error = pyqtSignal(str)

    def run(self):
        is_online, err = check_tidal_status()
        if err:
            self.error.emit(f"Error checking Tidal status: {err}")
        self.status_updated.emit(is_online)

class DeezerStatusChecker(QThread):
    status_updated = pyqtSignal(bool)
    error = pyqtSignal(str)

    def run(self):
        is_online, err = check_deezer_status()
        if err:
            self.error.emit(f"Error checking Deezer status: {err}")
        self.status_updated.emit(is_online)

class ServiceComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIconSize(QSize(16, 16))
        self.setItemDelegate(ServiceStatusDelegate())
        self.setup_items()
        
        self.tidal_status_checker = TidalStatusChecker()
        self.tidal_status_checker.status_updated.connect(self.update_tidal_status)
        self.tidal_status_checker.error.connect(lambda e: print(f"Tidal status check error: {e}"))
        self.tidal_status_checker.start()

        self.tidal_status_timer = QTimer(self)
        self.tidal_status_timer.timeout.connect(self.refresh_tidal_status)
        self.tidal_status_timer.start(60000)
        
        self.deezer_status_checker = DeezerStatusChecker()
        self.deezer_status_checker.status_updated.connect(self.update_deezer_status)
        self.deezer_status_checker.error.connect(lambda e: print(f"Deezer status check error: {e}"))
        self.deezer_status_checker.start()

        self.deezer_status_timer = QTimer(self)
        self.deezer_status_timer.timeout.connect(self.refresh_deezer_status)
        self.deezer_status_timer.start(60000)  
        
    def setup_items(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.services = [
            {'id': 'tidal', 'name': 'Tidal', 'icon': 'icons/tidal.png', 'online': False},
            {'id': 'deezer', 'name': 'Deezer', 'icon': 'icons/deezer.png', 'online': False}
        ]
        
        for service in self.services:
            icon_path = os.path.join(current_dir, service['icon'])
            if not os.path.exists(icon_path):
                self.create_placeholder_icon(icon_path)
            
            icon = QIcon(icon_path)
            
            self.addItem(icon, service['name'])
            item_index = self.count() - 1
            self.setItemData(item_index, service['id'], Qt.ItemDataRole.UserRole + 1)
            self.setItemData(item_index, service, Qt.ItemDataRole.UserRole)
    def create_placeholder_icon(self, path):
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        pixmap.save(path)
    
    def update_tidal_status(self, is_online):
        for i in range(self.count()):
            service_id = self.itemData(i, Qt.ItemDataRole.UserRole + 1)
            if service_id == 'tidal':
                service_data = self.itemData(i, Qt.ItemDataRole.UserRole)
                if isinstance(service_data, dict):
                    service_data['online'] = is_online
                    self.setItemData(i, service_data, Qt.ItemDataRole.UserRole)
                break
        self.update()
    
    def refresh_tidal_status(self):
        if hasattr(self, 'tidal_status_checker') and self.tidal_status_checker.isRunning():
            self.tidal_status_checker.quit()
            self.tidal_status_checker.wait()
        
        self.tidal_status_checker = TidalStatusChecker()
        self.tidal_status_checker.status_updated.connect(self.update_tidal_status)
        self.tidal_status_checker.error.connect(lambda e: print(f"Tidal status check error: {e}"))
        self.tidal_status_checker.start()
    
    def update_deezer_status(self, is_online):
        for i in range(self.count()):
            service_id = self.itemData(i, Qt.ItemDataRole.UserRole + 1)
            if service_id == 'deezer':
                service_data = self.itemData(i, Qt.ItemDataRole.UserRole)
                if isinstance(service_data, dict):
                    service_data['online'] = is_online
                    self.setItemData(i, service_data, Qt.ItemDataRole.UserRole)
                break
        self.update()
    
    def refresh_deezer_status(self):
        if hasattr(self, 'deezer_status_checker') and self.deezer_status_checker.isRunning():
            self.deezer_status_checker.quit()
            self.deezer_status_checker.wait()
        
        self.deezer_status_checker = DeezerStatusChecker()
        self.deezer_status_checker.status_updated.connect(self.update_deezer_status)
        self.deezer_status_checker.error.connect(lambda e: print(f"Deezer status check error: {e}"))
        self.deezer_status_checker.start()
        
    def currentData(self, role=Qt.ItemDataRole.UserRole + 1):
        return super().currentData(role)

class SpotiFLACGUI(QWidget):
    def __init__(
        self,
        *,
        settings_repo: Optional[SettingsRepository] = None,
        theme_manager: Optional[ThemeManager] = None,
    ) -> None:
        super().__init__()
        self.current_version = "5.3"
        self.tracks = []
        self.all_tracks = []  
        self.successful_downloads = []
        self.reset_state()
        
        self.spotify_service = SpotifyMetadataService()
        self.settings_repo = settings_repo or SettingsRepository()
        self.app_settings: AppSettings = self.settings_repo.load()
        self.theme_manager = theme_manager or ThemeManager(self.settings_repo)
        self.download_controller = DownloadController(self.spotify_service)
        self.download_controller.metadata_finished.connect(self.on_metadata_fetched)
        self.download_controller.metadata_error.connect(self.on_metadata_error)
        self.download_controller.download_progress.connect(self.update_progress)
        self.download_controller.download_finished.connect(self.on_download_finished)
        self.download_controller.secret_progress.connect(self.handle_secret_progress)
        self.download_controller.secret_finished.connect(self.on_scrape_finished)
        
        self.last_output_path = self.app_settings.output_path
        self.last_url = self.app_settings.spotify_url
        
        self.filename_format = self.app_settings.filename_format
        self.use_track_numbers = self.app_settings.use_track_numbers
        self.use_artist_subfolders = self.app_settings.use_artist_subfolders
        self.use_album_subfolders = self.app_settings.use_album_subfolders
        self.service = self.app_settings.service
        self.tidal_api = self.app_settings.tidal_api
        if not self.tidal_api or self.tidal_api == 'https://hifi.401658.xyz':
            self.tidal_api = 'auto'
            self._update_settings(tidal_api=self.tidal_api)
        self.deezer_fallback_enabled = self.app_settings.deezer_fallback
        self.check_for_updates = self.app_settings.check_for_updates
        self.current_theme_color = self.theme_manager.current_color
        self.track_list_format = self.app_settings.track_list_format
        self.date_format = self.app_settings.date_format
        
        self.elapsed_time = QTime(0, 0, 0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_cover_loaded)

        self.init_settings_controls()

        self.initUI()
        self.theme_manager.apply_theme(QApplication.instance())
        
    def _update_settings(self, **changes: object) -> None:
        if not changes:
            return
        self.settings_repo.update_values(**changes)
        for key, value in changes.items():
            if hasattr(self.app_settings, key):
                setattr(self.app_settings, key, value)

    def reset_state(self):
        """Reset application state to initial values."""
        self.tracks = []
        self.all_tracks = []
        self.successful_downloads = []
        self.skipped_downloads = []
        self.is_single_track = False
        self.is_album = False
        self.is_playlist = False
        self.album_or_playlist_name = ""

    def reset_ui(self):
        """Reset UI elements to initial state."""
        if hasattr(self, 'track_list'):
            self.track_list.clear()
        if hasattr(self, 'info_widget'):
            self.reset_info_widget()
            self.info_widget.hide()
        if hasattr(self, 'search_input'):
            self.search_input.clear()
        if hasattr(self, 'download_btn'):
            self.download_btn.setEnabled(False)
        self.hide_track_buttons()

    def set_combobox_value(self, combobox, target_value):
        for i in range(combobox.count()):
            if combobox.itemData(i, Qt.ItemDataRole.UserRole + 1) == target_value:
                combobox.setCurrentIndex(i)
                return True
            if combobox.itemData(i, Qt.ItemDataRole.UserRole) == target_value:
                combobox.setCurrentIndex(i)
                return True
        return False

    def filter_tracks(self):
        search_text = self.search_input.text().lower().strip()
        
        if not search_text:
            self.tracks = self.all_tracks.copy()
        else:
            self.tracks = [
                track for track in self.all_tracks
                if (search_text in track.title.lower() or 
                    search_text in track.artists.lower() or 
                    search_text in track.album.lower())
            ]
        
        self.update_track_list_display()

    def format_track_date(self, release_date):
        if not release_date:
            return ""
        
        try:
            if len(release_date) == 4:
                date_obj = datetime.strptime(release_date, "%Y")
                if self.date_format == "yyyy":
                    return date_obj.strftime('%Y')
                else:
                    return date_obj.strftime('%Y')
            elif len(release_date) == 7:
                date_obj = datetime.strptime(release_date, "%Y-%m")
                if self.date_format == "dd_mm_yyyy":
                    return date_obj.strftime('%m-%Y')
                elif self.date_format == "yyyy_mm_dd":
                    return date_obj.strftime('%Y-%m')
                else:
                    return date_obj.strftime('%Y')
            else:
                date_obj = datetime.strptime(release_date, "%Y-%m-%d")
                if self.date_format == "dd_mm_yyyy":
                    return date_obj.strftime('%d-%m-%Y')
                elif self.date_format == "yyyy_mm_dd":
                    return date_obj.strftime('%Y-%m-%d')
                else:
                    return date_obj.strftime('%Y')
        except ValueError:
            return release_date

    def format_duration(self, duration_ms: int) -> str:
        """Format duration from milliseconds to MM:SS format.
        
        Args:
            duration_ms: Duration in milliseconds
            
        Returns:
            Formatted duration string (e.g., "3:45")
        """
        if not duration_ms:
            return "0:00"
        
        total_seconds = duration_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"

    def update_track_list_display(self):
        self.track_list.clear()
        for i, track in enumerate(self.tracks, 1):
            duration = self.format_duration(track.duration_ms)
            formatted_date = self.format_track_date(track.release_date)
            
            if self.track_list_format == "artist_track_date_duration":
                display_parts = [f"{i}. {track.artists} - {track.title}"]
                if formatted_date:
                    display_parts.append(formatted_date)
                display_parts.append(duration)
                display_text = " • ".join(display_parts)
            elif self.track_list_format == "track_artist_date_duration":
                display_parts = [f"{i}. {track.title} - {track.artists}"]
                if formatted_date:
                    display_parts.append(formatted_date)
                display_parts.append(duration)
                display_text = " • ".join(display_parts)
            elif self.track_list_format == "track_artist_date":
                display_parts = [f"{i}. {track.title} - {track.artists}"]
                if formatted_date:
                    display_parts.append(formatted_date)
                display_text = " • ".join(display_parts)
            elif self.track_list_format == "artist_track_date":
                display_parts = [f"{i}. {track.artists} - {track.title}"]
                if formatted_date:
                    display_parts.append(formatted_date)
                display_text = " • ".join(display_parts)
            elif self.track_list_format == "track_artist_duration":
                display_text = f"{i}. {track.title} - {track.artists} • {duration}"
            elif self.track_list_format == "artist_track_duration":
                display_text = f"{i}. {track.artists} - {track.title} • {duration}"
            elif self.track_list_format == "track_artist":
                display_text = f"{i}. {track.title} - {track.artists}"
            elif self.track_list_format == "artist_track":
                display_text = f"{i}. {track.artists} - {track.title}"
            else:
                display_parts = [f"{i}. {track.title} - {track.artists}"]
                if formatted_date:
                    display_parts.append(formatted_date)
                display_parts.append(duration)
                display_text = " • ".join(display_parts)
            
            self.track_list.addItem(display_text)

    def browse_output(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_dir.setText(directory)
            self.save_settings()

    def setup_tabs(self):
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.dashboard_tab = DashboardTab(self)
        self.tab_widget.addTab(self.dashboard_tab.widget, "Dashboard")
        self.hide_track_buttons()
        
        self.process_tab = ProcessTab(self)
        self.tab_widget.addTab(self.process_tab.widget, "Process")

        self.settings_tab = SettingsTab(self)
        self.tab_widget.addTab(self.settings_tab.widget, "Settings")

        self.theme_tab = ThemeTab(self)
        self.tab_widget.addTab(self.theme_tab.widget, "Theme")

        self.about_tab = AboutTab(self)
        self.tab_widget.addTab(self.about_tab.widget, "About")

        self.theme_manager.refresh_button_icons(self)

    def get_themed_icon(self, icon_name):
        return self.theme_manager.themed_icon(icon_name)

    def initUI(self):
        self.setWindowTitle('SpotiFLAC')
        self.setFixedWidth(650)
        self.setMinimumHeight(350)  
        
        icon_path = os.path.join(os.path.dirname(__file__), "icons", "icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.main_layout = QVBoxLayout()
        
        self.setup_spotify_section()
        self.setup_tabs()
        
        self.setLayout(self.main_layout)

    def init_settings_controls(self):
        self.service_dropdown = ServiceComboBox()
        self.service_dropdown.setFixedWidth(100)
        self.service_dropdown.currentIndexChanged.connect(self.on_service_changed)

        self.tidal_api_label = QLabel('API Instances:')
        self.tidal_api_label.setFixedWidth(85)

        self.tidal_api_dropdown = QComboBox()
        self.tidal_api_dropdown.setItemDelegate(TidalAPIDelegate())
        self.tidal_api_dropdown.addItem("Auto Fallback (recommended)", "auto")
        self.tidal_api_dropdown.currentIndexChanged.connect(self.on_tidal_api_changed)

        self.refresh_api_btn = QPushButton('Refresh')
        self.refresh_api_btn.setFixedWidth(80)
        self.refresh_api_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_api_btn.clicked.connect(self.refresh_tidal_apis)

        self.tidal_api_hint_label = QLabel(
            "Tip: Auto fallback selects working Tidal proxies automatically. "
            "Recommended because individual instances often go offline."
        )
        self.tidal_api_hint_label.setWordWrap(True)
        self.tidal_api_hint_label.setStyleSheet("color: #ff9800; font-size: 11px;")

        self.deezer_fallback_checkbox = QCheckBox('Try Deezer automatically if Tidal fails')
        self.deezer_fallback_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.deezer_fallback_checkbox.setChecked(self.deezer_fallback_enabled)
        self.deezer_fallback_checkbox.toggled.connect(self.save_deezer_fallback_setting)

        # Apply persisted selections
        self.set_combobox_value(self.service_dropdown, self.service)
        self.update_tidal_api_visibility()
        self.set_combobox_value(self.tidal_api_dropdown, self.tidal_api)

    def setup_spotify_section(self):
        spotify_layout = QHBoxLayout()
        spotify_label = QLabel('Spotify URL:')
        spotify_label.setFixedWidth(100)
        
        self.spotify_url = QLineEdit()
        self.spotify_url.setPlaceholderText("Enter Spotify URL")
        self.spotify_url.setClearButtonEnabled(True)
        self.spotify_url.setText(self.last_url)
        self.spotify_url.textChanged.connect(self.save_url)
        
        self.fetch_btn = QPushButton('Fetch')
        self.fetch_btn.setFixedWidth(80)
        self.fetch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fetch_btn.clicked.connect(self.fetch_tracks)
        
        spotify_layout.addWidget(spotify_label)
        spotify_layout.addWidget(self.spotify_url)
        spotify_layout.addWidget(self.fetch_btn)
        self.main_layout.addLayout(spotify_layout)

    def change_theme_color(self, color, clicked_btn=None):
        self.theme_manager.change_color(self, color, clicked_btn)

    def refresh_button_icons(self):
        self.theme_manager.refresh_button_icons(self)

    def setup_about_tab(self):
        about_tab = QWidget()
        about_layout = QVBoxLayout()
        about_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.setSpacing(15)

        sections = [
            ("Check for Updates", "Check", "https://github.com/afkarxyz/SpotiFLAC/releases"),
            ("Report an Issue", "Report", "https://github.com/afkarxyz/SpotiFLAC/issues")
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
            button.clicked.connect(lambda _, url=url: QDesktopServices.openUrl(QUrl(url if url.startswith(('http://', 'https://')) else f'https://{url}')))
            section_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)

            about_layout.addWidget(section_widget)

        footer_label = QLabel(f"v{self.current_version} | October 2025")
        about_layout.addWidget(footer_label, alignment=Qt.AlignmentFlag.AlignCenter)

        about_tab.setLayout(about_layout)
        self.tab_widget.addTab(about_tab, "About")

    def on_service_changed(self, index):
        service = self.service_dropdown.currentData()
        if not service:
            return
        self.service = service
        self._update_settings(service=service)
        if hasattr(self, 'log_output') and self.log_output:
            self.log_output.append(f"Service changed to: {self.service_dropdown.currentText()}")
        self.update_tidal_api_visibility()

    def update_tidal_api_visibility(self):
        is_tidal = self.service == 'tidal'
        self.tidal_api_label.setVisible(is_tidal)
        self.tidal_api_dropdown.setVisible(is_tidal)
        self.refresh_api_btn.setVisible(is_tidal)
        if hasattr(self, 'tidal_api_hint_label'):
            self.tidal_api_hint_label.setVisible(is_tidal)
        if hasattr(self, 'deezer_fallback_checkbox'):
            self.deezer_fallback_checkbox.setVisible(is_tidal)

    def on_tidal_api_changed(self, index):
        selected_api = self.tidal_api_dropdown.currentData()
        if selected_api:
            self.tidal_api = selected_api
            self._update_settings(tidal_api=selected_api)
            self.log_output.append(f"API Instance changed to: {self.tidal_api_dropdown.currentText()}")
    
    def refresh_tidal_apis(self):
        try:
            self.log_output.append("Fetching available API instances...")
            apis = get_available_tidal_apis()
            
            while self.tidal_api_dropdown.count() > 1:
                self.tidal_api_dropdown.removeItem(1)
            
            if apis:
                for api in apis:
                    url = api.get('url', '')
                    uptime = api.get('uptime', 0)
                    avg_time = api.get('avg_response_time', 0)
                    status = "UP" if api.get('last_check', {}).get('success') else "DOWN"
                    
                    domain = url.replace('https://', '').replace('http://', '')
                    label = f"{domain} ({uptime:.0f}%, {avg_time}ms)"
                    
                    status_data = {
                        'status': status,
                        'uptime': uptime,
                        'avg_time': avg_time
                    }
                    
                    self.tidal_api_dropdown.addItem(label, url)
                    item_index = self.tidal_api_dropdown.count() - 1
                    self.tidal_api_dropdown.setItemData(item_index, status_data, Qt.ItemDataRole.UserRole + 1)
                
                self.log_output.append(f"Found {len(apis)} available API instances")
            else:
                self.log_output.append("No APIs found, using default")
        except Exception as e:
            self.log_output.append(f"Error fetching APIs: {str(e)}")

    def save_url(self):
        value = self.spotify_url.text().strip()
        self.last_url = value
        self._update_settings(spotify_url=value)
        
    def save_filename_format(self):
        if self.artist_title_radio.isChecked():
            self.filename_format = "artist_title"
        elif self.title_only_radio.isChecked():
            self.filename_format = "title_only"
        else:
            self.filename_format = "title_artist"
        self._update_settings(filename_format=self.filename_format)
        
    def save_track_numbering(self):
        self.use_track_numbers = self.track_number_checkbox.isChecked()
        self._update_settings(use_track_numbers=self.use_track_numbers)
    
    def save_artist_subfolder_setting(self):
        self.use_artist_subfolders = self.artist_subfolder_checkbox.isChecked()
        self._update_settings(use_artist_subfolders=self.use_artist_subfolders)
    
    def save_album_subfolder_setting(self):
        self.use_album_subfolders = self.album_subfolder_checkbox.isChecked()
        self._update_settings(use_album_subfolders=self.use_album_subfolders)
    
    def save_deezer_fallback_setting(self):
        self.deezer_fallback_enabled = self.deezer_fallback_checkbox.isChecked()
        self._update_settings(deezer_fallback=self.deezer_fallback_enabled)
    
    def save_track_list_format(self):
        format_value = self.track_list_format_dropdown.currentData()
        self.track_list_format = format_value
        self._update_settings(track_list_format=format_value)
        if self.tracks:
            self.update_track_list_display()
    
    def save_date_format(self):
        format_value = self.date_format_dropdown.currentData()
        self.date_format = format_value
        self._update_settings(date_format=format_value)
        if self.tracks:
            self.update_track_list_display()
    
    def save_settings(self):
        out_path = self.output_dir.text().strip()
        self.last_output_path = out_path
        self._update_settings(output_path=out_path)
        self.log_output.append("Settings saved successfully!")
                        
    def update_timer(self):
        self.elapsed_time = self.elapsed_time.addSecs(1)
        self.time_label.setText(self.elapsed_time.toString("hh:mm:ss"))
                        
    def fetch_tracks(self):
        url = self.spotify_url.text().strip()
        
        if not url:
            self.log_output.append('Warning: Please enter a Spotify URL.')
            return

        try:
            if hasattr(self, 'fix_error_btn') and self.fix_error_btn.isVisible():
                self.fix_error_btn.hide()
            
            self.reset_state()
            self.reset_ui()
            
            self.log_output.append('Just a moment. Fetching metadata...')
            self.tab_widget.setCurrentWidget(self.process_tab.widget)
            
            self.download_controller.fetch_metadata(url)
            
        except Exception as e:
            self.log_output.append(f'Error: Failed to start metadata fetch: {str(e)}')
    
    def on_metadata_fetched(self, metadata):
        try:
            url_info = self.spotify_service.parse_url(self.spotify_url.text().strip())
            
            if url_info["type"] == "track":
                self.handle_track_metadata(metadata["track"])
            elif url_info["type"] == "album":
                self.handle_album_metadata(metadata)
            elif url_info["type"] == "playlist":
                self.handle_playlist_metadata(metadata)
            elif url_info["type"] == "artist_discography":
                self.handle_discography_metadata(metadata)
            elif url_info["type"] == "artist":
                self.handle_artist_metadata(metadata)
                
            self.update_button_states()
            self.tab_widget.setCurrentIndex(0)
        except Exception as e:
            self.log_output.append(f'Error: {str(e)}')
    
    def on_metadata_error(self, error_message):
        self.log_output.append(f'Error: {error_message}')
        
        if "Failed to get raw data" in error_message or "Failed to fetch secrets" in error_message or "Failed to get access token" in error_message:
            if not hasattr(self, 'fix_error_btn') or not self.fix_error_btn.isVisible():
                self.show_fix_error_button()
    
    def show_fix_error_button(self):
        if hasattr(self, 'fix_error_btn'):
            self.fix_error_btn.show()
    
    def fix_error_action(self):
        self.fix_error_btn.setEnabled(False)
        self.fix_error_btn.setText("Fixing...")
        
        self.download_controller.start_secret_fix()

    def handle_secret_progress(self, message):
        self.log_output.append(message)

    def on_scrape_finished(self, success, message):
        self.log_output.append(message)

        if hasattr(self, 'fix_error_btn'):
            self.fix_error_btn.setEnabled(True)
            self.fix_error_btn.setText("Fix Error")

            if success:
                self.fix_error_btn.hide()

        if success:
            url = self.spotify_url.text().strip()
            if url:
                self.log_output.append("Retrying fetch...")
                QTimer.singleShot(1000, self.fetch_tracks)

    def handle_track_metadata(self, track_data):
        track_id = track_data["external_urls"].split("/")[-1]
        
        track = Track(
            external_urls=track_data["external_urls"],
            title=track_data["name"],
            artists=track_data["artists"],
            album=track_data["album_name"],
            track_number=1,
            duration_ms=track_data.get("duration_ms", 0),
            id=track_id,
            isrc=track_data.get("isrc", ""),
            release_date=track_data.get("release_date", "")
        )
        
        self.tracks = [track]
        self.all_tracks = [track]
        self.is_single_track = True
        self.is_album = self.is_playlist = False
        self.album_or_playlist_name = f"{self.tracks[0].title} - {self.tracks[0].artists}"
        
        metadata = {
            'title': track_data["name"],
            'artists': track_data["artists"],
            'releaseDate': track_data["release_date"],
            'cover': track_data["images"],
            'duration_ms': track_data.get("duration_ms", 0)
        }
        self.update_display_after_fetch(metadata)

    def handle_album_metadata(self, album_data):
        self.album_or_playlist_name = album_data["album_info"]["name"]
        self.tracks = []
        
        for track in album_data["track_list"]:
            track_id = track["external_urls"].split("/")[-1]
            
            self.tracks.append(Track(
                external_urls=track["external_urls"],
                title=track["name"],
                artists=track["artists"],
                album=self.album_or_playlist_name,
                track_number=track["track_number"],
                duration_ms=track.get("duration_ms", 0),
                id=track_id,
                isrc=track.get("isrc", ""),
                release_date=track.get("release_date", "")
            ))
        
        self.all_tracks = self.tracks.copy()
        self.is_album = True
        self.is_playlist = self.is_single_track = False
        
        metadata = {
            'title': album_data["album_info"]["name"],
            'artists': album_data["album_info"]["artists"],
            'releaseDate': album_data["album_info"]["release_date"],
            'cover': album_data["album_info"]["images"],
            'total_tracks': album_data["album_info"]["total_tracks"]
        }
        self.update_display_after_fetch(metadata)

    def handle_playlist_metadata(self, playlist_data):
        # Handle both legacy and new API format
        if "playlist_info" in playlist_data:
            # Legacy format
            self.album_or_playlist_name = playlist_data["playlist_info"]["owner"]["name"]
            track_list = playlist_data["track_list"]
        else:
            # New API format
            self.album_or_playlist_name = playlist_data.get("name", "Unknown Playlist")
            track_list = playlist_data.get("tracks", {}).get("items", [])
        
        self.tracks = []
        
        for track_item in track_list:
            # Handle both formats
            if "track" in track_item:
                # New format (playlist items have 'track' key)
                track = track_item["track"]
            else:
                # Legacy format
                track = track_item
            
            if not track:
                continue
                
            track_id = track.get("external_urls", {}).get("spotify", "").split("/")[-1] if isinstance(track.get("external_urls"), dict) else track.get("external_urls", "").split("/")[-1]
            artists = ', '.join([a.get('name', '') for a in track.get('artists', [])]) if isinstance(track.get('artists'), list) else track.get('artists', '')
            
            self.tracks.append(Track(
                external_urls=track.get("external_urls", {}).get("spotify", "") if isinstance(track.get("external_urls"), dict) else track.get("external_urls", ""),
                title=track.get("name", ""),
                artists=artists,
                album=track.get("album", {}).get("name", "") if isinstance(track.get("album"), dict) else track.get("album_name", ""),
                track_number=track.get("track_number", len(self.tracks) + 1),
                duration_ms=track.get("duration_ms", 0),
                id=track_id,
                isrc=track.get("external_ids", {}).get("isrc", "") if isinstance(track.get("external_ids"), dict) else track.get("isrc", ""),
                release_date=track.get("album", {}).get("release_date", "") if isinstance(track.get("album"), dict) else track.get("release_date", "")
            ))
        
        self.all_tracks = self.tracks.copy()
        self.is_playlist = True
        self.is_album = self.is_single_track = False
        
        # Build metadata from available data
        if "playlist_info" in playlist_data:
            # Legacy format
            metadata = {
                'title': playlist_data["playlist_info"]["owner"]["name"],
                'artists': playlist_data["playlist_info"]["owner"]["display_name"],
                'cover': playlist_data["playlist_info"]["owner"]["images"],
                'followers': playlist_data["playlist_info"]["followers"]["total"],
                'total_tracks': playlist_data["playlist_info"]["tracks"]["total"]
            }
        else:
            # New format
            metadata = {
                'title': playlist_data.get("name", ""),
                'artists': playlist_data.get("owner", {}).get("display_name", ""),
                'cover': playlist_data.get("images", [{}])[0].get("url", "") if playlist_data.get("images") else "",
                'followers': playlist_data.get("followers", {}).get("total", 0),
                'total_tracks': playlist_data.get("tracks", {}).get("total", len(self.tracks))
            }
        
        self.update_display_after_fetch(metadata)

    def handle_discography_metadata(self, discography_data):
        artist_info = discography_data["artist_info"]
        self.album_or_playlist_name = f"{artist_info['name']} - Discography ({artist_info['discography_type'].title()})"
        self.tracks = []
        
        for track in discography_data["track_list"]:
            track_id = track["external_urls"].split("/")[-1] if track.get("external_urls") else ""
            
            self.tracks.append(Track(
                external_urls=track.get("external_urls", ""),
                title=track["name"],
                artists=track["artists"],
                album=track["album_name"],
                track_number=track.get("track_number", len(self.tracks) + 1),
                duration_ms=track.get("duration_ms", 0),
                id=track_id,
                isrc=track.get("isrc", ""),
                release_date=track.get("release_date", "")
            ))
        
        self.all_tracks = self.tracks.copy()
        self.is_playlist = True
        self.is_album = self.is_single_track = False
        
        metadata = {
            'title': f"{artist_info['name']} - Discography",
            'artists': f"{artist_info['discography_type'].title()} • {artist_info['total_albums']} albums",
            'cover': artist_info["images"],
            'followers': artist_info.get("followers", 0),
            'total_tracks': len(self.tracks),
            'discography_type': artist_info['discography_type']
        }
        self.update_display_after_fetch(metadata)

    def handle_artist_metadata(self, artist_data):
        self.reset_state()
        
        metadata = {
            'title': artist_data["artist"]["name"],
            'artists': f"Followers: {artist_data['artist']['followers']:,}",
            'cover': artist_data["artist"]["images"],
            'followers': artist_data["artist"]["followers"],
            'genres': artist_data["artist"].get("genres", [])
        }
        
        self.update_info_widget_artist_only(metadata)

    def update_display_after_fetch(self, metadata):
        self.track_list.setVisible(not self.is_single_track)
        
        if not self.is_single_track:
            self.search_widget.show()
            self.update_track_list_display()
        else:
            self.search_widget.hide()
        
        self.update_info_widget(metadata)

    def update_info_widget(self, metadata):
        self.title_label.setText(metadata['title'])
        
        if self.is_single_track or self.is_album:
            artists = metadata['artists'] if isinstance(metadata['artists'], list) else metadata['artists'].split(", ")
            label_text = "Artists" if len(artists) > 1 else "Artist"
            artists_text = ", ".join(artists)
            self.artists_label.setText(f"<b>{label_text}</b> {artists_text}")
        else:
            self.artists_label.setText(f"<b>Owner</b> {metadata['artists']}")
        
        if self.is_playlist and 'followers' in metadata:
            self.followers_label.setText(f"<b>Followers</b> {metadata['followers']:,}")
            self.followers_label.show()
        else:
            self.followers_label.hide()
        
        if metadata.get('releaseDate'):
            try:
                release_date = metadata['releaseDate']
                if len(release_date) == 4:
                    date_obj = datetime.strptime(release_date, "%Y")
                elif len(release_date) == 7:
                    date_obj = datetime.strptime(release_date, "%Y-%m")
                else:
                    date_obj = datetime.strptime(release_date, "%Y-%m-%d")
                
                formatted_date = date_obj.strftime("%d-%m-%Y")
                self.release_date_label.setText(f"<b>Released</b> {formatted_date}")
                self.release_date_label.show()
            except ValueError:
                self.release_date_label.setText(f"<b>Released</b> {metadata['releaseDate']}")
                self.release_date_label.show()
        else:
            self.release_date_label.hide()
        
        if self.is_single_track:
            duration = self.format_duration(metadata.get('duration_ms', 0))
            self.type_label.setText(f"<b>Duration</b> {duration}")
        elif self.is_album:
            total_tracks = metadata.get('total_tracks', 0)
            self.type_label.setText(f"<b>Album</b> • {total_tracks} tracks")
        elif self.is_playlist:
            total_tracks = metadata.get('total_tracks', 0)
            if metadata.get('discography_type'):
                discography_type = metadata['discography_type'].title()
                self.type_label.setText(f"<b>Discography ({discography_type})</b> • {total_tracks} tracks")
            else:
                self.type_label.setText(f"<b>Playlist</b> • {total_tracks} tracks")
        
        self.network_manager.get(QNetworkRequest(QUrl(metadata['cover'])))
        
        self.info_widget.show()

    def update_info_widget_artist_only(self, metadata):
        self.title_label.setText(metadata['title'])
        self.artists_label.setText(f"<b>Followers</b> {metadata['followers']:,}")
        
        if metadata.get('genres'):
            genres_text = ", ".join(metadata['genres'][:3])
            if len(metadata['genres']) > 3:
                genres_text += f" (+{len(metadata['genres']) - 3} more)"
            self.followers_label.setText(f"<b>Genres</b> {genres_text}")
            self.followers_label.show()
        else:
            self.followers_label.hide()
        
        self.release_date_label.hide()
        self.type_label.setText("<b>Artist Profile</b> • No tracks available for download")
        
        self.network_manager.get(QNetworkRequest(QUrl(metadata['cover'])))
        
        self.track_list.hide()
        self.search_widget.hide()
        self.hide_track_buttons()
        
        self.info_widget.show()

    def reset_info_widget(self):
        self.title_label.clear()
        self.artists_label.clear()
        self.followers_label.clear()
        self.release_date_label.clear()
        self.type_label.clear()
        self.cover_label.clear()
        self.info_widget.hide()

    def on_cover_loaded(self, reply):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self.cover_label.setPixmap(pixmap)

    def update_button_states(self):
        if self.is_single_track:
            for btn in [self.download_btn, self.delete_btn]:
                btn.hide()
            
            self.single_track_container.show()
            
            self.single_download_btn.setEnabled(True)
            self.single_delete_btn.setEnabled(True)
            
        else:
            self.single_track_container.hide()
            
            self.download_btn.show()
            self.delete_btn.show()
            
            self.download_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)

    def hide_track_buttons(self):
        buttons = [
            self.download_btn,
            self.delete_btn
        ]
        for btn in buttons:
            btn.hide()
        
        if hasattr(self, 'single_track_container'):
            self.single_track_container.hide()

    def download_tracks_action(self):
        if self.is_single_track:
            self.start_download([0])
        else:
            selected_items = self.track_list.selectedItems()
            
            if not selected_items:
                reply = QMessageBox.question(
                    self,
                    'Confirm Download All',
                    f'No tracks selected. Download all {len(self.tracks)} tracks?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.start_download(range(len(self.tracks)))
            else:
                selected_indices = [self.track_list.row(item) for item in selected_items]
                self.start_download(selected_indices)
    
    def start_download(self, indices):
        self.log_output.clear()
        raw_outpath = self.output_dir.text().strip()
        outpath = os.path.normpath(raw_outpath)
        if not os.path.exists(outpath):
            self.log_output.append('Warning: Invalid output directory.')
            return

        tracks_to_download = self.tracks if self.is_single_track else [self.tracks[i] for i in indices]

        if self.is_album or self.is_playlist:
            name = self.album_or_playlist_name.strip()
            folder_name = re.sub(r'[<>:"/\\|?*]', '_', name)
            folder_name = folder_name.rstrip('. ')
            outpath = os.path.join(outpath, folder_name)
            os.makedirs(outpath, exist_ok=True)

        try:
            self.download_controller.start_download(
                tracks_to_download,
                outpath,
                is_single_track=self.is_single_track,
                is_album=self.is_album,
                is_playlist=self.is_playlist,
                album_or_playlist_name=self.album_or_playlist_name,
                filename_format=self.filename_format,
                use_track_numbers=self.use_track_numbers,
                use_artist_subfolders=self.use_artist_subfolders,
                use_album_subfolders=self.use_album_subfolders,
                service=self.service,
                tidal_api_url=self.tidal_api,
                deezer_fallback_enabled=self.deezer_fallback_enabled,
            )
            self.start_timer()
            self.update_ui_for_download_start()
        except Exception as e:
            self.log_output.append(f"Error: An error occurred while starting the download: {str(e)}")
    
    def update_ui_for_download_start(self):
        self.download_btn.setEnabled(False)
        
        if hasattr(self, 'single_download_btn'):
            self.single_download_btn.setEnabled(False)
        if hasattr(self, 'single_delete_btn'):
            self.single_delete_btn.setEnabled(False)
            
        self.stop_btn.show()
        self.pause_resume_btn.show()
        self.remove_successful_btn.hide()
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        
        self.tab_widget.setCurrentWidget(self.process_tab.widget)

    def update_progress(self, message, percentage):
        self.log_output.append(message)
        self.log_output.moveCursor(QTextCursor.MoveOperation.End)
        if percentage > 0:
            self.progress_bar.setValue(percentage)

    def stop_download(self):
        self.download_controller.stop_download()
        self.stop_timer()
        self.on_download_finished(True, "Download stopped by user.", [], [], [])
        
    def on_download_finished(self, success, message, failed_tracks, successful_tracks=None, skipped_tracks=None):
        self.progress_bar.hide()
        self.stop_btn.hide()
        self.pause_resume_btn.hide()
        self.pause_resume_btn.setText('Pause')
        self.stop_timer()
        
        if successful_tracks is not None:
            self.successful_downloads = successful_tracks
        if skipped_tracks is not None:
            self.skipped_downloads = skipped_tracks
        
        if (hasattr(self, 'successful_downloads') and self.successful_downloads) or (hasattr(self, 'skipped_downloads') and self.skipped_downloads):
            self.remove_successful_btn.show()
        else:
            self.remove_successful_btn.hide()
        
        self.download_btn.setEnabled(True)
        
        if hasattr(self, 'single_download_btn'):
            self.single_download_btn.setEnabled(True)
        if hasattr(self, 'single_delete_btn'):
            self.single_delete_btn.setEnabled(True)
        
        if success:
            self.log_output.append(f"\nStatus: {message}")
            if failed_tracks:
                self.log_output.append("\nFailed downloads:")
                for title, artists, error in failed_tracks:
                    self.log_output.append(f"• {title} - {artists}")
                    self.log_output.append(f"  Error: {error}\n")
        else:
            self.log_output.append(f"Error: {message}")

        self.tab_widget.setCurrentWidget(self.process_tab.widget)
    
    def toggle_pause_resume(self):
        if self.pause_resume_btn.isVisible():
            if self.pause_resume_btn.text() == 'Resume':
                self.download_controller.resume_download()
                self.pause_resume_btn.setText('Pause')
                self.timer.start(1000)
            else:
                self.download_controller.pause_download()
                self.pause_resume_btn.setText('Resume')

    def remove_successful_downloads(self):
        successful_tracks = getattr(self, 'successful_downloads', [])
        skipped_tracks = getattr(self, 'skipped_downloads', [])
        
        if not successful_tracks and not skipped_tracks:
            self.log_output.append("No downloaded or skipped tracks to remove.")
            return
        
        tracks_to_remove = []
        
        for track in self.tracks:
            for successful_track in successful_tracks:
                if (track.title == successful_track.title and 
                    track.artists == successful_track.artists and
                    track.album == successful_track.album):
                    tracks_to_remove.append(track)
                    break
        
        for track in self.tracks:
            for skipped_track in skipped_tracks:
                if (track.title == skipped_track.title and 
                    track.artists == skipped_track.artists and
                    track.album == skipped_track.album):
                    if track not in tracks_to_remove:
                        tracks_to_remove.append(track)
                    break
        
        if tracks_to_remove:
            for track in tracks_to_remove:
                if track in self.tracks:
                    self.tracks.remove(track)
                if track in self.all_tracks:
                    self.all_tracks.remove(track)
            
            self.update_track_list_display()
            successful_count = len([t for t in tracks_to_remove if t in successful_tracks])
            skipped_count = len([t for t in tracks_to_remove if t in skipped_tracks])
            
            message = f"Removed {len(tracks_to_remove)} tracks from the list"
            if successful_count > 0:
                message += f" ({successful_count} downloaded"
            if skipped_count > 0:
                message += f", {skipped_count} already existed" if successful_count > 0 else f" ({skipped_count} already existed"
            if successful_count > 0 or skipped_count > 0:
                message += ")"
            
            self.log_output.append(message + ".")
            self.tab_widget.setCurrentIndex(0)
        else:
            self.log_output.append("No matching tracks found in the current list.")
        
        self.remove_successful_btn.hide()

    def delete_tracks(self):
        if self.is_single_track:
            self.reset_state()
            self.reset_ui()
        else:
            selected_items = self.track_list.selectedItems()
            
            if not selected_items:
                reply = QMessageBox.question(
                    self,
                    'Confirm Delete All',
                    f'No tracks selected. Delete all {len(self.tracks)} tracks?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.reset_state()
                    self.reset_ui()
            else:
                selected_indices = [self.track_list.row(item) for item in selected_items]
                tracks_to_remove = [self.tracks[i] for i in selected_indices]
                
                for track in tracks_to_remove:
                    if track in self.tracks:
                        self.tracks.remove(track)
                    if track in self.all_tracks:
                        self.all_tracks.remove(track)
                
                self.update_track_list_display()
        self.tab_widget.setCurrentIndex(0)

    def start_timer(self):
        self.elapsed_time = QTime(0, 0, 0)
        self.time_label.setText("00:00:00")
        self.time_label.show()
        self.timer.start(1000)
    
    def stop_timer(self):
        self.timer.stop()
        self.time_label.hide()

    def closeEvent(self, event):
        if hasattr(self, 'timer'):
            self.timer.stop()
        
        if hasattr(self, 'service_dropdown'):
            for attr_name in ['tidal_status_checker', 'deezer_status_checker']:
                if hasattr(self.service_dropdown, attr_name):
                    checker = getattr(self.service_dropdown, attr_name)
                    if checker.isRunning():
                        checker.quit()
                        checker.wait()
        
        if hasattr(self, 'download_controller'):
            self.download_controller.cleanup()
        
        event.accept()

if __name__ == '__main__':
    try:
        if sys.platform == "win32":
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception as e:
        pass
        
    app = QApplication(sys.argv)
    ex = SpotiFLACGUI()
    ex.show()
    sys.exit(app.exec())