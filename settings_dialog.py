"""
settings_dialog.py - Settings window
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QSpinBox, QFormLayout, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from theme import get_theme


class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.theme = get_theme(self.settings.get("theme", "dark"))
        self.setWindowTitle("PingGuard Settings")
        self.setModal(True)
        self.setFixedWidth(440)
        self.setStyleSheet(self._stylesheet())
        self._build_ui()

    def _stylesheet(self):
        t = self.theme
        return f"""
            QDialog {{ background: {t['bg']}; color: {t['text']}; }}
            QLabel {{ color: {t['text']}; }}
            QSpinBox, QComboBox {{
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
            QCheckBox {{ color: {t['text']}; font-size: 12px; spacing: 8px; }}
            QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 3px;
                background: {t['surface']}; border: 1px solid {t['border']}; }}
            QCheckBox::indicator:checked {{ background: {t['accent']}; border-color: {t['accent_hover']}; }}
        """

    def _build_ui(self):
        t = self.theme
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("⚙ Settings")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {t['text_bright']};")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        form.setContentsMargins(0, 4, 0, 4)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Dark", "dark")
        self.theme_combo.addItem("Light", "light")
        current_theme = self.settings.get("theme", "dark")
        self.theme_combo.setCurrentIndex(0 if current_theme == "dark" else 1)
        form.addRow("Appearance:", self.theme_combo)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(30, 600)
        self.interval_spin.setSuffix(" seconds")
        self.interval_spin.setValue(self.settings.get("auto_check_interval", 120))
        form.addRow("Auto-check every:", self.interval_spin)

        self.alert_spin = QSpinBox()
        self.alert_spin.setRange(50, 500)
        self.alert_spin.setSuffix(" ms")
        self.alert_spin.setValue(self.settings.get("alert_threshold_ms", 150))
        form.addRow("Alert if ping above:", self.alert_spin)

        self.region_combo = QComboBox()
        for r in ["EU", "NA", "Asia", "SA", "OCE"]:
            self.region_combo.addItem(r)
        self.region_combo.setCurrentText(self.settings.get("user_region", "EU"))
        form.addRow("Your Region:", self.region_combo)

        layout.addLayout(form)

        self.sound_check = QCheckBox("Play sound on high ping / disconnect")
        self.sound_check.setChecked(self.settings.get("sound_enabled", True))
        layout.addWidget(self.sound_check)

        self.notif_check = QCheckBox("Show desktop notifications")
        self.notif_check.setChecked(self.settings.get("notifications_enabled", True))
        layout.addWidget(self.notif_check)

        self.minimized_check = QCheckBox("Start minimized to tray")
        self.minimized_check.setChecked(self.settings.get("start_minimized", True))
        layout.addWidget(self.minimized_check)

        self.startup_check = QCheckBox("Start with Windows")
        self.startup_check.setChecked(self.settings.get("start_with_windows", False))
        layout.addWidget(self.startup_check)

        layout.addSpacing(4)

        # Save / Cancel
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(36)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{ background: {t['surface']}; color: {t['text']}; border: 1px solid {t['border']};
                          border-radius: 6px; padding: 2px 16px; }}
            QPushButton:hover {{ background: {t['surface_hover']}; }}
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save Settings")
        save_btn.setFixedHeight(36)
        save_btn.setStyleSheet(f"""
            QPushButton {{ background: {t['accent']}; color: white; border: none;
                          border-radius: 6px; padding: 2px 16px; font-weight: bold; }}
            QPushButton:hover {{ background: {t['accent_hover']}; }}
        """)
        save_btn.clicked.connect(self._save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _save(self):
        self.settings.set("theme", self.theme_combo.currentData())
        self.settings.set("auto_check_interval", self.interval_spin.value())
        self.settings.set("alert_threshold_ms", self.alert_spin.value())
        self.settings.set("user_region", self.region_combo.currentText())
        self.settings.set("sound_enabled", self.sound_check.isChecked())
        self.settings.set("notifications_enabled", self.notif_check.isChecked())
        self.settings.set("start_minimized", self.minimized_check.isChecked())
        self.settings.set("start_with_windows", self.startup_check.isChecked())
        self.accept()
