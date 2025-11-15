from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton


class ThemeTab:
    """Theme tab UI with color palette buttons."""

    def __init__(self, owner) -> None:
        self.owner = owner
        self.widget = QWidget()
        self._build()

    def _build(self) -> None:
        owner = self.owner
        layout = QVBoxLayout(self.widget)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)

        theme_label = QLabel('Theme')
        theme_label.setStyleSheet("font-weight: bold; margin-top: 8px; margin-bottom: 5px;")
        layout.addWidget(theme_label)

        grid_layout = QVBoxLayout()
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        owner.color_buttons = {}

        for row_palettes in self._palette_rows():
            row_layout = QHBoxLayout()
            row_layout.setSpacing(15)
            for palette_name, colors in row_palettes:
                row_layout.addLayout(self._build_palette_column(palette_name, colors))
            grid_layout.addLayout(row_layout)

        layout.addLayout(grid_layout)
        layout.addStretch()

    def _build_palette_column(self, palette_name: str, colors: list[tuple[str, str]]) -> QVBoxLayout:
        owner = self.owner
        column_layout = QVBoxLayout()
        column_layout.setSpacing(3)

        palette_label = QLabel(palette_name)
        palette_label.setStyleSheet("margin-bottom: 2px;")
        palette_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column_layout.addWidget(palette_label)

        color_buttons_layout = QHBoxLayout()
        color_buttons_layout.setSpacing(3)

        for color_hex, color_name in colors:
            color_btn = QPushButton()
            color_btn.setFixedSize(18, 18)
            is_current = color_hex == self.owner.current_theme_color
            border_style = "2px solid #fff" if is_current else "none"
            color_btn.setStyleSheet(
                f"QPushButton {{ background-color: {color_hex}; border: {border_style}; border-radius: 9px; }}"
                "QPushButton:hover { border: 2px solid #fff; }"
                "QPushButton:pressed { border: 2px solid #fff; }"
            )
            color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            color_btn.setToolTip(f"{palette_name} {color_name}\n{color_hex}")
            color_btn.clicked.connect(
                lambda checked, c=color_hex, btn=color_btn: self.owner.change_theme_color(c, btn)
            )
            owner.color_buttons[color_hex] = color_btn
            color_buttons_layout.addWidget(color_btn)

        column_layout.addLayout(color_buttons_layout)
        return column_layout

    @staticmethod
    def _palette_rows() -> list[list[tuple[str, list[tuple[str, str]]]]]:
        return [
            [
                ("Pink", [("#FFC5C5", "100"), ("#FF99CC", "200"), ("#FF80AB", "300"), ("#FF4081", "400"), ("#F50057", "500"), ("#E91E63", "600"), ("#D81B60", "700"), ("#C51162", "800"), ("#B71C1C", "900"), ("#FF80AB", "A100"), ("#FF4081", "A200"), ("#F50057", "A400"), ("#E91E63", "A700")]),
                ("Purple", [("#C7B8EA", "100"), ("#A377D0", "200"), ("#8F5AE2", "300"), ("#7B1FA2", "400"), ("#6A1B9A", "500"), ("#4A148C", "600"), ("#3A0CA3", "700"), ("#2E115F", "800"), ("#1A0CA6", "900"), ("#B388FF", "A100"), ("#7C4DFF", "A200"), ("#651FFF", "A400"), ("#6200EA", "A700")]),
                ("Deep Orange", [("#FFD7BE", "100"), ("#FFC080", "200"), ("#FFA07A", "300"), ("#FF8C00", "400"), ("#FF6F00", "500"), ("#FF3D00", "600"), ("#DD2C00", "700"), ("#C51162", "800"), ("#FFC107", "900"), ("#FFA000", "A100"), ("#FF8F00", "A200"), ("#FF6F00", "A400"), ("#FF3D00", "A700")]),
            ],
            [
                ("Deep Purple", [("#D1C4E9", "100"), ("#B39DDB", "200"), ("#9575CD", "300"), ("#7E57C2", "400"), ("#673AB7", "500"), ("#5E35B1", "600"), ("#512DA8", "700"), ("#4527A0", "800"), ("#311B92", "900"), ("#B388FF", "A100"), ("#7C4DFF", "A200"), ("#651FFF", "A400"), ("#6200EA", "A700")]),
                ("Indigo", [("#C5CAE9", "100"), ("#9FA8DA", "200"), ("#7986CB", "300"), ("#5C6BC0", "400"), ("#3F51B5", "500"), ("#3949AB", "600"), ("#303F9F", "700"), ("#283593", "800"), ("#1A237E", "900"), ("#8C9EFF", "A100"), ("#536DFE", "A200"), ("#3D5AFE", "A400"), ("#304FFE", "A700")]),
                ("Blue", [("#BBDEFB", "100"), ("#90CAF9", "200"), ("#64B5F6", "300"), ("#42A5F5", "400"), ("#2196F3", "500"), ("#1E88E5", "600"), ("#1976D2", "700"), ("#1565C0", "800"), ("#0D47A1", "900"), ("#82B1FF", "A100"), ("#448AFF", "A200"), ("#2979FF", "A400"), ("#2962FF", "A700")]),
            ],
            [
                ("Light Blue", [("#B3E5FC", "100"), ("#81D4FA", "200"), ("#4FC3F7", "300"), ("#29B6F6", "400"), ("#03A9F4", "500"), ("#039BE5", "600"), ("#0288D1", "700"), ("#0277BD", "800"), ("#01579B", "900"), ("#80D8FF", "A100"), ("#40C4FF", "A200"), ("#00B0FF", "A400"), ("#0091EA", "A700")]),
                ("Cyan", [("#B2EBF2", "100"), ("#80DEEA", "200"), ("#4DD0E1", "300"), ("#26C6DA", "400"), ("#00BCD4", "500"), ("#00ACC1", "600"), ("#0097A7", "700"), ("#00838F", "800"), ("#006064", "900"), ("#84FFFF", "A100"), ("#18FFFF", "A200"), ("#00E5FF", "A400"), ("#00B8D4", "A700")]),
                ("Teal", [("#B2DFDB", "100"), ("#80CBC4", "200"), ("#4DB6AC", "300"), ("#26A69A", "400"), ("#009688", "500"), ("#00897B", "600"), ("#00796B", "700"), ("#00695C", "800"), ("#004D40", "900"), ("#A7FFEB", "A100"), ("#64FFDA", "A200"), ("#1DE9B6", "A400"), ("#00BFA5", "A700")]),
            ],
            [
                ("Green", [("#C8E6C9", "100"), ("#A5D6A7", "200"), ("#81C784", "300"), ("#66BB6A", "400"), ("#4CAF50", "500"), ("#43A047", "600"), ("#388E3C", "700"), ("#2E7D32", "800"), ("#1B5E20", "900"), ("#B9F6CA", "A100"), ("#69F0AE", "A200"), ("#00E676", "A400"), ("#00C853", "A700")]),
                ("Light Green", [("#DCEDC8", "100"), ("#C5E1A5", "200"), ("#AED581", "300"), ("#9CCC65", "400"), ("#8BC34A", "500"), ("#7CB342", "600"), ("#689F38", "700"), ("#558B2F", "800"), ("#33691E", "900"), ("#CCFF90", "A100"), ("#B2FF59", "A200"), ("#76FF03", "A400"), ("#64DD17", "A700")]),
                ("Lime", [("#F0F4C3", "100"), ("#E6EE9C", "200"), ("#DCE775", "300"), ("#D4E157", "400"), ("#CDDC39", "500"), ("#C0CA33", "600"), ("#AFB42B", "700"), ("#9E9D24", "800"), ("#827717", "900"), ("#F4FF81", "A100"), ("#EEFF41", "A200"), ("#C6FF00", "A400"), ("#AEEA00", "A700")]),
            ],
            [
                ("Yellow", [("#FFF9C4", "100"), ("#FFF59D", "200"), ("#FFF176", "300"), ("#FFEE58", "400"), ("#FFEB3B", "500"), ("#FDD835", "600"), ("#FBC02D", "700"), ("#F9A825", "800"), ("#F57F17", "900"), ("#FFFF8D", "A100"), ("#FFFF00", "A200"), ("#FFEA00", "A400"), ("#FFD600", "A700")]),
                ("Amber", [("#FFECB3", "100"), ("#FFE082", "200"), ("#FFD54F", "300"), ("#FFCA28", "400"), ("#FFC107", "500"), ("#FFB300", "600"), ("#FFA000", "700"), ("#FF8F00", "800"), ("#FF6F00", "900"), ("#FFE57F", "A100"), ("#FFD740", "A200"), ("#FFC400", "A400"), ("#FFAB00", "A700")]),
                ("Orange", [("#FFE0B2", "100"), ("#FFCC80", "200"), ("#FFB74D", "300"), ("#FFA726", "400"), ("#FF9800", "500"), ("#FB8C00", "600"), ("#F57C00", "700"), ("#EF6C00", "800"), ("#E65100", "900"), ("#FFD180", "A100"), ("#FFAB40", "A200"), ("#FF9100", "A400"), ("#FF6D00", "A700")]),
            ],
        ]
