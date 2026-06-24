"""
add_game_dialog.py - Dialog for adding a custom game
"""
import os

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSpinBox, QFormLayout, QFrame, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from game_detector import detect_all_games
from constants import DISCORD_REPORT_WEBHOOK
from reporter import send_game_request


CATEGORIES = ["FPS", "MOBA", "MMO", "ARPG", "Battle Royale", "Sports", "Sandbox", "Open World", "Other"]
ICONS = ["🎮", "🎯", "🔫", "⚔️", "🏆", "🛡️", "💥", "🚀", "⚡", "🌙", "💀", "🗺️", "⚽", "🚗", "🪟", "🌌"]

# Always the first item in the dropdown once the scan completes - lets
# the user explicitly skip it and type a name by hand below.
_MANUAL_ENTRY_OPTION = "— Type the name myself —"
_SCANNING_PLACEHOLDER = "Scanning for installed games..."
_NONE_FOUND_PLACEHOLDER = "No installed games detected"


class GameDetectionWorker(QThread):
    """
    Runs game_detector.detect_all_games() off the UI thread.

    Scanning the registry and disk across four launchers can take a
    noticeable moment on a PC with a large Steam library, so this must
    never block the dialog from opening or responding.
    """
    finished_scanning = pyqtSignal(list)

    def run(self):
        try:
            games = detect_all_games()
        except Exception:
            # detect_all_games() already guards every individual
            # detector internally, but if something still slips
            # through, fall back to an empty list rather than crash -
            # the dialog still works fine with manual entry only.
            games = []
        self.finished_scanning.emit(games)


class ReportSendWorker(QThread):
    """
    Sends a game request to Discord off the UI thread. send_game_request()
    does a blocking network call with a 5-second timeout - on a slow
    connection that's a 5-second frozen dialog if run directly on the
    UI thread, so it gets its own thread here.
    """
    finished_sending = pyqtSignal(bool, str)

    def __init__(self, webhook_url, game_name, parent=None):
        super().__init__(parent)
        self.webhook_url = webhook_url
        self.game_name = game_name

    def run(self):
        success, message = send_game_request(self.webhook_url, self.game_name)
        self.finished_sending.emit(success, message)


class AddGameDialog(QDialog):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.detected_games = []  # populated once the background scan finishes
        self._last_detected_install_path = None
        self.setWindowTitle("Add Game")
        self.setModal(True)
        self.setFixedSize(420, 555)
        self.setStyleSheet(self._stylesheet())
        self._build_ui()
        self._start_detection_scan()

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

        # --- Detected games dropdown ---
        detected_label = QLabel("Installed Games:")
        detected_label.setStyleSheet(f"color: {t['text_muted']}; font-size: 11px; font-weight: bold;")
        layout.addWidget(detected_label)

        self.detected_combo = QComboBox()
        self.detected_combo.addItem(_SCANNING_PLACEHOLDER)
        self.detected_combo.setEnabled(False)
        self.detected_combo.currentIndexChanged.connect(self._on_detected_game_selected)
        layout.addWidget(self.detected_combo)

        hint = QLabel("Don't see your game? Just type its name below instead.")
        hint.setStyleSheet(f"color: {t['text_muted']}; font-size: 10px;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"background: {t['border']}; max-height: 1px;")
        layout.addWidget(divider)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. My Game")
        form.addRow("Game Name:", self.name_input)

        self.exe_input = QLineEdit()
        self.exe_input.setPlaceholderText("e.g. mygame.exe")
        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedWidth(70)
        browse_btn.setStyleSheet(f"""
            QPushButton {{ background: {t['surface']}; color: {t['text']}; border: 1px solid {t['border']};
                          border-radius: 6px; padding: 2px 8px; font-size: 11px; }}
            QPushButton:hover {{ background: {t['surface_hover']}; }}
        """)
        browse_btn.clicked.connect(self._browse_for_exe)
        exe_row = QHBoxLayout()
        exe_row.addWidget(self.exe_input)
        exe_row.addWidget(browse_btn)
        form.addRow("Process (.exe):", exe_row)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("e.g. store.steampowered.com")
        self.host_input.setToolTip(
            "The website address PingGuard will test the connection to — "
            "found on the game's official site, support page, or status page."
        )
        form.addRow("Server Address:", self.host_input)

        host_hint = QLabel(
            "Not the game's name — this is checked on the game's site or support page. "
            "Not sure? Use the report button below instead of guessing."
        )
        host_hint.setStyleSheet(f"color: {t['text_muted']}; font-size: 10px;")
        host_hint.setWordWrap(True)
        form.addRow("", host_hint)

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

        # --- Game request report ---
        report_row = QHBoxLayout()
        self.report_btn = QPushButton("🎮 Tell the dev I couldn't find this game")
        self.report_btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {t['text_muted']}; border: none;
                          font-size: 10px; text-decoration: underline; text-align: left; }}
            QPushButton:hover {{ color: {t['text']}; }}
        """)
        self.report_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.report_btn.clicked.connect(self._send_game_request)
        report_row.addWidget(self.report_btn)
        report_row.addStretch()
        layout.addLayout(report_row)

        self.report_status = QLabel("")
        self.report_status.setStyleSheet(f"color: {t['text_muted']}; font-size: 10px;")
        self.report_status.setWordWrap(True)
        layout.addWidget(self.report_status)

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

    # ------------------------------------------------------------------
    # Detection scan
    # ------------------------------------------------------------------

    def _start_detection_scan(self):
        self._detection_thread = GameDetectionWorker(self)
        self._detection_thread.finished_scanning.connect(self._on_scan_finished)
        self._detection_thread.start()

    def _on_scan_finished(self, games):
        self.detected_games = games
        self.detected_combo.blockSignals(True)
        self.detected_combo.clear()
        self.detected_combo.addItem(_MANUAL_ENTRY_OPTION)
        if games:
            for game in games:
                self.detected_combo.addItem(f"{game.name}  ({game.source})")
        else:
            self.detected_combo.addItem(_NONE_FOUND_PLACEHOLDER)
        self.detected_combo.setEnabled(True)
        self.detected_combo.blockSignals(False)

    def _on_detected_game_selected(self, index):
        # Index 0 is always "Type the name myself". If the scan found
        # nothing, index 1 is the "none detected" placeholder, which
        # also has no matching entry in self.detected_games - guarded
        # the same way so it's a no-op rather than an index error.
        game_index = index - 1
        if game_index < 0 or game_index >= len(self.detected_games):
            return
        game = self.detected_games[game_index]
        self.name_input.setText(game.name)
        self._last_detected_install_path = game.install_path

    def _browse_for_exe(self):
        start_dir = self._last_detected_install_path or ""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select the game's .exe", start_dir, "Executable Files (*.exe)"
        )
        if path:
            self.exe_input.setText(os.path.basename(path))

    # ------------------------------------------------------------------
    # Game request reporting
    # ------------------------------------------------------------------

    def _send_game_request(self):
        name = self.name_input.text().strip()
        if not name:
            self.report_status.setText("Type the game's name above first.")
            return
        if not DISCORD_REPORT_WEBHOOK:
            self.report_status.setText("Reporting isn't available right now.")
            return

        self.report_btn.setEnabled(False)
        self.report_status.setText("Sending...")

        self._report_thread = ReportSendWorker(DISCORD_REPORT_WEBHOOK, name, self)
        self._report_thread.finished_sending.connect(self._on_report_sent)
        self._report_thread.start()

    def _on_report_sent(self, success, message):
        if success:
            self.report_status.setText("Thanks! We'll look into adding it.")
        else:
            self.report_status.setText("Couldn't send — try again later.")
            self.report_btn.setEnabled(True)

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
