from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QProgressBar,
    QLabel,
)


class ProcessTab:
    """Process tab UI encapsulation."""

    def __init__(self, owner) -> None:
        self.owner = owner
        self.widget = QWidget()
        self._build()

    def _build(self) -> None:
        owner = self.owner
        layout = QVBoxLayout()
        layout.setSpacing(5)

        owner.log_output = QTextEdit()
        owner.log_output.setReadOnly(True)
        layout.addWidget(owner.log_output)

        fix_error_layout = QHBoxLayout()
        fix_error_layout.addStretch()
        owner.fix_error_btn = QPushButton(' Fix Error')
        owner.fix_error_btn.setIcon(owner.get_themed_icon('tool.svg'))
        owner.fix_error_btn.setFixedWidth(120)
        owner.fix_error_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        owner.fix_error_btn.clicked.connect(owner.fix_error_action)
        owner.fix_error_btn.hide()
        fix_error_layout.addWidget(owner.fix_error_btn)
        fix_error_layout.addStretch()
        layout.addLayout(fix_error_layout)

        progress_time_layout = QVBoxLayout()
        progress_time_layout.setSpacing(2)
        owner.progress_bar = QProgressBar()
        progress_time_layout.addWidget(owner.progress_bar)

        owner.time_label = QLabel("00:00:00")
        owner.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_time_layout.addWidget(owner.time_label)
        layout.addLayout(progress_time_layout)

        control_layout = QHBoxLayout()
        owner.stop_btn = QPushButton('Stop')
        owner.pause_resume_btn = QPushButton('Pause')
        owner.stop_btn.setFixedWidth(120)
        owner.pause_resume_btn.setFixedWidth(120)
        owner.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        owner.pause_resume_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        owner.stop_btn.clicked.connect(owner.stop_download)
        owner.pause_resume_btn.clicked.connect(owner.toggle_pause_resume)

        owner.remove_successful_btn = QPushButton(' Remove Finished Tracks')
        owner.remove_successful_btn.setIcon(owner.get_themed_icon('circle-x.svg'))
        owner.remove_successful_btn.setFixedWidth(200)
        owner.remove_successful_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        owner.remove_successful_btn.clicked.connect(owner.remove_successful_downloads)

        control_layout.addStretch()
        control_layout.addWidget(owner.stop_btn)
        control_layout.addWidget(owner.pause_resume_btn)
        control_layout.addWidget(owner.remove_successful_btn)
        control_layout.addStretch()
        layout.addLayout(control_layout)

        owner.progress_bar.hide()
        owner.time_label.hide()
        owner.stop_btn.hide()
        owner.pause_resume_btn.hide()
        owner.remove_successful_btn.hide()

        self.widget.setLayout(layout)
