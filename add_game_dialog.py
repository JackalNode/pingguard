"""
add_game_dialog.py - Dialog for adding a custom game
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSpinBox, QFormLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


CATEGORIES = ["FPS", "MOBA", "MMO", "ARPG", "Battle Royale", "Sports", "Sandbox", "Open World", "Other"]
ICONS = ["🎮", "🎯", "🔫", "⚔️", "🏆", "🛡️", "💥", "🚀", "⚡", "🌙", "💀", "🗺️", "⚽", "🚗", "🪟", "🌌"]


class AddGameDialog(QDialog):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setWindowTitle("Add Game")
        self.setModal(True)
        self.setFixedSize(420, 400)
        self.setStyleSheet(self._stylesheet())
        self._build_ui()

    def _stylesheet(self):
        t = self.theme
        return f"""
            QDialog {{ background: {t['bg']}; color: {t['text']}; }}
            QLabel {{ color: {t['text']}; }}
            QLineEdit, QComboBox, QSpinBox {{
                background: {t['surface']};
                border: 1px solid {t['border']};
                border-radius: 6px;
                padding: 4px 10px;
                min-height: 20px;
                color: {t['text']};
                font-size: 12px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background: {t['surface']};
                color: {t['text']};
                border: 1px solid {t['border']};
                selection-background-color: {t['accent']};
                selection-color: white;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border-color: {t['accent_hover']};
            }}
        """

    def _build_ui(self):
        t = self.theme
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Add a Game")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {t['text_bright']};")
        layout.addWidget(title)

        subtitle = QLabel("PingGuard will test the connection to this game's servers.")
        subtitle.setStyleSheet(f"color: {t['text_muted']}; font-size: 11px;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. My Game")
        form.addRow("Game Name:", self.name_input)

        self.exe_input = QLineEdit()
        self.exe_input.setPlaceholderText("e.g. mygame.exe")
        form.addRow("Process (.exe):", self.exe_input)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("e.g. api.mygame.com")
        form.addRow("Server Host:", self.host_input)

        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(443)
        form.addRow("Port:", self.port_input)

        self.category_input = QComboBox()
        for c in CATEGORIES:
            self.category_input.addItem(c)
        form.addRow("Category:", self.category_input)

        self.icon_input = QComboBox()
        for icon in ICONS:
            self.icon_input.addItem(icon)
        form.addRow("Icon:", self.icon_input)

        layout.addLayout(form)
        layout.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(36)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{ background: {t['surface']}; color: {t['text']}; border: 1px solid {t['border']};
                          border-radius: 6px; padding: 4px 16px; }}
            QPushButton:hover {{ background: {t['surface_hover']}; }}
        """)
        cancel_btn.clicked.connect(self.reject)

        add_btn = QPushButton("Add Game")
        add_btn.setFixedHeight(36)
        add_btn.setStyleSheet(f"""
            QPushButton {{ background: {t['accent']}; color: white; border: none;
                          border-radius: 6px; padding: 4px 16px; font-weight: bold; }}
            QPushButton:hover {{ background: {t['accent_hover']}; }}
        """)
        add_btn.clicked.connect(self.accept)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(add_btn)
        layout.addLayout(btn_row)

    def get_game_data(self):
        name = self.name_input.text().strip()
        host = self.host_input.text().strip()
        if not name or not host:
            return None
        return {
            "name": name,
            "exe": self.exe_input.text().strip(),
            "icon": self.icon_input.currentText(),
            "category": self.category_input.currentText(),
            "region_note": "Custom",
            "endpoints": [{"host": host, "port": self.port_input.value()}],
        }
