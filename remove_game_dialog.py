"""
remove_game_dialog.py - Dialog for removing (disabling) a monitored game
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


_PLACEHOLDER_OPTION = "— Select a game to remove —"


class RemoveGameDialog(QDialog):
    def __init__(self, theme, enabled_games, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.enabled_games = enabled_games
        self.setWindowTitle("Remove Game")
        self.setModal(True)
        self.setFixedSize(380, 220)
        self.setStyleSheet(self._stylesheet())
        self._build_ui()

    def _stylesheet(self):
        t = self.theme
        return f"""
            QDialog {{ background: {t['bg']}; color: {t['text']}; }}
            QLabel {{ color: {t['text']}; }}
            QComboBox {{
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
            QComboBox:focus {{
                border-color: {t['accent_hover']};
            }}
        """

    def _build_ui(self):
        t = self.theme
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Remove Game")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {t['text_bright']};")
        layout.addWidget(title)

        subtitle = QLabel(
            "Choose a game to stop monitoring. It won't be deleted — you "
            "can add it back anytime from + Add Game."
        )
        subtitle.setStyleSheet(f"color: {t['text_muted']}; font-size: 11px;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.game_combo = QComboBox()
        self.game_combo.addItem(_PLACEHOLDER_OPTION)
        for game in self.enabled_games:
            self.game_combo.addItem(game["name"])
        self.game_combo.currentIndexChanged.connect(self._on_selection_changed)
        layout.addWidget(self.game_combo)

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
        # Cancel is the dialog's real default button, and Confirm is
        # explicitly never auto/default - Enter must never be able to
        # trigger a removal from any widget's focus state, only cancel
        # or do nothing.
        cancel_btn.setDefault(True)
        cancel_btn.clicked.connect(self.reject)

        self.confirm_btn = QPushButton("Confirm")
        self.confirm_btn.setFixedHeight(36)
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.setAutoDefault(False)
        self.confirm_btn.setDefault(False)
        self.confirm_btn.setStyleSheet(f"""
            QPushButton {{ background: {t['btn_neutral_bg']}; color: {t['text']}; border: none;
                          border-radius: 6px; padding: 4px 16px; font-weight: bold; }}
            QPushButton:hover {{ background: {t['btn_neutral_hover']}; }}
            QPushButton:disabled {{ color: {t['text_dim']}; }}
        """)
        self.confirm_btn.clicked.connect(self.accept)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(self.confirm_btn)
        layout.addLayout(btn_row)

    def _on_selection_changed(self, index):
        self.confirm_btn.setEnabled(index > 0)

    def get_selected_game_name(self):
        index = self.game_combo.currentIndex()
        if index <= 0:
            return None
        return self.game_combo.currentText()
