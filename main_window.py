"""
main_window.py - The main PingGuard UI window
Shows all games with their ping status, history graph, controls.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QMessageBox, QDialog,
    QLineEdit, QComboBox, QCheckBox, QSpinBox, QTabWidget,
    QTextEdit, QFileDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QIcon, QPixmap, QBrush, QPolygonF, QPainterPath, QTransform
from PyQt6.QtCore import QPointF
from games import get_ping_status, DEFAULT_GAMES
from add_game_dialog import AddGameDialog
from report_dialog import ReportDialog
from constants import DISCORD_REPORT_WEBHOOK
from theme import get_theme
import datetime
import sys
import os


def resource_path(relative_path):
    """Get the absolute path to a bundled resource (works both in dev and
    in the PyInstaller-built .exe, where assets are unpacked to sys._MEIPASS)."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def make_gear_icon(color, size=18):
    """Draws a crisp vector gear/cog icon at any size and any color.
    Replaces relying on the unicode '⚙' glyph, whose appearance varies
    wildly (sometimes barely recognizable as a gear) depending on which
    font the OS falls back to render it with."""
    scale = 4  # draw oversized, then downscale for clean anti-aliased edges
    s = size * scale
    pm = QPixmap(s, s)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    cx, cy = s / 2, s / 2
    body_r = s * 0.30
    hole_r = s * 0.13
    tooth_w = s * 0.17
    tooth_h = s * 0.16
    tooth_dist = s * 0.34
    teeth = 8

    path = QPainterPath()
    path.addEllipse(QPointF(cx, cy), body_r, body_r)

    for i in range(teeth):
        angle = (360 / teeth) * i
        tooth = QPainterPath()
        tooth.addRoundedRect(-tooth_w / 2, -tooth_dist - tooth_h / 2, tooth_w, tooth_h, 3, 3)
        transform = QTransform()
        transform.translate(cx, cy)
        transform.rotate(angle)
        path = path.united(transform.map(tooth))

    hole = QPainterPath()
    hole.addEllipse(QPointF(cx, cy), hole_r, hole_r)
    path = path.subtracted(hole)

    painter.setBrush(QBrush(QColor(color)))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawPath(path)
    painter.end()

    pm = pm.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    return QIcon(pm)


class PingBar(QWidget):
    """Mini ping history sparkline graph."""
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.history = []
        self.setMinimumSize(80, 30)
        self.setMaximumSize(120, 30)

    def set_history(self, history):
        self.history = [h.get("ms") for h in history[-20:] if h.get("ms") is not None]
        self.update()

    def paintEvent(self, event):
        if not self.history or len(self.history) < 2:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        margin = 3
        max_val = max(max(self.history), 100)
        min_val = 0

        points = []
        for i, val in enumerate(self.history):
            x = margin + (i / (len(self.history) - 1)) * (w - 2 * margin)
            y = h - margin - ((val - min_val) / (max_val - min_val)) * (h - 2 * margin)
            points.append((x, y))

        _, color = get_ping_status(self.history[-1], self.theme)
        pen = QPen(QColor(color), 1.5)
        painter.setPen(pen)

        for i in range(len(points) - 1):
            painter.drawLine(int(points[i][0]), int(points[i][1]),
                           int(points[i+1][0]), int(points[i+1][1]))


class PingDot(QWidget):
    """Status dot."""
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.color = theme["ping_unknown"]
        self.setFixedSize(14, 14)

    def set_color(self, color):
        self.color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(self.color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 10, 10)


class PingHistoryChart(QWidget):
    """Expanded full ping history chart with filled area, gridlines, stats."""
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.history = []   # list of ms values (ints)
        self.color = theme["ping_excellent"]
        self.setMinimumHeight(110)
        self.setMaximumHeight(110)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_history(self, history, color):
        self.history = [h.get("ms") for h in history if h.get("ms") is not None]
        self.color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        t = self.theme

        w, h = self.width(), self.height()
        left_margin = 28
        right_margin = 8
        top_margin = 10
        bottom_margin = 22   # room for stats text

        chart_w = w - left_margin - right_margin
        chart_h = h - top_margin - bottom_margin

        # Background
        painter.fillRect(0, 0, w, h, QColor(t["bg"]))

        if not self.history or len(self.history) < 2:
            painter.setPen(QColor(t["text_dim"]))
            painter.drawText(0, 0, w, h, Qt.AlignmentFlag.AlignCenter, "No data yet")
            return

        max_val = max(max(self.history), 100)
        min_val = 0

        # Gridlines + Y labels
        grid_pen = QPen(QColor(t["chart_grid"]), 1)
        grid_pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        label_font = QFont("Consolas", 7)
        painter.setFont(label_font)

        for grid_val in [0, 50, 100, 150, 200]:
            if grid_val > max_val * 1.1:
                continue
            y = top_margin + chart_h - (grid_val / max_val) * chart_h
            painter.setPen(grid_pen)
            painter.drawLine(left_margin, int(y), left_margin + chart_w, int(y))
            painter.setPen(QColor(t["text_dim"]))
            painter.drawText(0, int(y) - 6, left_margin - 2, 12,
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                             str(grid_val))

        # Build points
        points = []
        for i, val in enumerate(self.history):
            x = left_margin + (i / (len(self.history) - 1)) * chart_w
            y = top_margin + chart_h - ((val - min_val) / (max_val - min_val)) * chart_h
            points.append(QPointF(x, y))

        # Filled area under the line
        fill_color = QColor(self.color)
        fill_color.setAlpha(35)
        poly = QPolygonF()
        poly.append(QPointF(points[0].x(), top_margin + chart_h))
        for p in points:
            poly.append(p)
        poly.append(QPointF(points[-1].x(), top_margin + chart_h))
        painter.setBrush(QBrush(fill_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(poly)

        # Line
        line_pen = QPen(QColor(self.color), 1.8)
        line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(line_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i + 1])

        # Dot at last point
        painter.setBrush(QBrush(QColor(self.color)))
        painter.setPen(Qt.PenStyle.NoPen)
        lp = points[-1]
        painter.drawEllipse(lp, 3.5, 3.5)

        # Stats bar at bottom
        stats_y = h - bottom_margin + 6
        painter.setFont(QFont("Consolas", 8))
        painter.setPen(QColor(t["chart_stats_text"]))

        mn = min(self.history)
        avg = int(sum(self.history) / len(self.history))
        mx = max(self.history)
        samples = len(self.history)

        stats_text = f"min {mn}ms    avg {avg}ms    max {mx}ms    samples {samples}"
        painter.drawText(left_margin, stats_y, chart_w, 14,
                         Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         stats_text)


class GameRow(QFrame):
    """A single game row — click to expand/collapse ping history chart."""
    report_clicked = pyqtSignal(dict)

    def __init__(self, game, theme, parent=None):
        super().__init__(parent)
        self.game = game
        self.theme = theme
        self._expanded = False
        self._history = []
        self._last_ms = None
        self._last_color = theme["ping_unknown"]

        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            GameRow {{
                background: {theme['surface']};
                border-radius: 8px;
                margin: 2px 0;
            }}
            GameRow:hover {{
                background: {theme['row_hover']};
            }}
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Top row ──────────────────────────────────────────────
        top_widget = QWidget()
        top_widget.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(top_widget)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        self.dot = PingDot(theme)
        layout.addWidget(self.dot)

        icon_label = QLabel(game.get("icon", "🎮"))
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        icon_label.setFixedWidth(28)
        layout.addWidget(icon_label)

        name_layout = QVBoxLayout()
        name_layout.setSpacing(1)
        self.name_label = QLabel(game["name"])
        self.name_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.name_label.setStyleSheet(f"color: {theme['text']};")
        self.category_label = QLabel(game.get("category", "") + " • " + game.get("region_note", ""))
        self.category_label.setFont(QFont("Segoe UI", 8))
        self.category_label.setStyleSheet(f"color: {theme['text_muted']};")
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.category_label)
        layout.addLayout(name_layout)
        layout.addStretch()

        self.spark = PingBar(theme)
        layout.addWidget(self.spark)

        self.ping_label = QLabel("—")
        self.ping_label.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        self.ping_label.setStyleSheet(f"color: {theme['text_faint']};")
        self.ping_label.setFixedWidth(65)
        self.ping_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.ping_label)

        self.report_btn = QPushButton("⚠")
        self.report_btn.setToolTip("Report this game isn't working correctly")
        self.report_btn.setFixedSize(28, 28)
        self.report_btn.setVisible(False)
        self.report_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {theme['text_faint']};
                font-size: 14px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background: {theme['report_hover_bg']};
                color: {theme['warning']};
            }}
        """)
        self.report_btn.clicked.connect(self._on_report_clicked)
        layout.addWidget(self.report_btn)

        outer.addWidget(top_widget)

        # ── Expanded chart panel ──────────────────────────────────
        self.chart_panel = QWidget()
        self.chart_panel.setStyleSheet("background: transparent;")
        chart_layout = QVBoxLayout(self.chart_panel)
        chart_layout.setContentsMargins(12, 0, 12, 8)
        chart_layout.setSpacing(2)

        self.chart_label = QLabel("▴ ping history")
        self.chart_label.setFont(QFont("Segoe UI", 7))
        self.chart_label.setStyleSheet(f"color: {theme['text_dim']};")
        chart_layout.addWidget(self.chart_label)

        self.chart = PingHistoryChart(theme)
        chart_layout.addWidget(self.chart)

        self.chart_panel.hide()
        outer.addWidget(self.chart_panel)

    def _on_report_clicked(self):
        self.report_clicked.emit(self.game)

    def mousePressEvent(self, event):
        # Don't toggle if clicking the report button
        if self.report_btn.underMouse():
            return
        self._toggle_expand()
        super().mousePressEvent(event)

    def _toggle_expand(self):
        self._expanded = not self._expanded
        if self._expanded:
            self.chart.set_history(self._history, self._last_color)
            self.chart_panel.show()
            self.chart_label.setText("▾ ping history")
        else:
            self.chart_panel.hide()
            self.chart_label.setText("▴ ping history")

    def enterEvent(self, event):
        self.report_btn.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.report_btn.setVisible(False)
        super().leaveEvent(event)

    def update_ping(self, ms, history):
        status, color = get_ping_status(ms, self.theme)
        self._last_ms = ms
        self._last_color = color
        self._history = history

        self.dot.set_color(color)
        self.spark.set_history(history)

        if ms is not None:
            self.ping_label.setText(f"{ms} ms")
            self.ping_label.setStyleSheet(f"color: {color};")
        else:
            self.ping_label.setText("—")
            self.ping_label.setStyleSheet(f"color: {self.theme['text_very_dim']};")

        # Refresh chart if expanded
        if self._expanded:
            self.chart.set_history(history, color)


class MainWindow(QMainWindow):
    check_now_requested = pyqtSignal()
    settings_requested = pyqtSignal()

    def __init__(self, game_manager, settings, ping_worker):
        super().__init__()
        self.game_manager = game_manager
        self.settings = settings
        self.ping_worker = ping_worker
        self.game_rows = {}
        self.theme = get_theme(self.settings.get("theme", "dark"))

        self.setWindowTitle("PingGuard")
        self.setWindowIcon(QIcon(resource_path("assets/icon.ico")))
        self.setMinimumSize(520, 600)
        self.resize(560, 680)
        self.setStyleSheet(self._stylesheet())

        self._build_ui()

    def apply_theme(self):
        """Re-read the active theme from settings and rebuild the UI in the
        new colors immediately — no restart required."""
        self.theme = get_theme(self.settings.get("theme", "dark"))
        self.setStyleSheet(self._stylesheet())
        old_central = self.centralWidget()
        self.game_rows = {}
        self._build_ui()
        if old_central:
            old_central.deleteLater()

    def _build_ui(self):
        t = self.theme
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)

        # Header
        header = QHBoxLayout()
        title = QLabel("🎮 PingGuard")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {t['text_bright']};")
        header.addWidget(title)
        header.addStretch()

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"color: {t['text_muted']}; font-size: 11px;")
        header.addWidget(self.status_label)

        self.check_btn = QPushButton("Check Now")
        self.check_btn.setFixedHeight(36)
        self.check_btn.setStyleSheet(self._button_style(t['accent'], t['accent_hover'], text_color="white"))
        self.check_btn.clicked.connect(self._on_check_now)
        header.addWidget(self.check_btn)

        settings_btn = QPushButton()
        settings_btn.setIcon(make_gear_icon(t['text']))
        settings_btn.setIconSize(QSize(18, 18))
        settings_btn.setFixedSize(34, 34)
        settings_btn.setToolTip("Settings")
        settings_btn.setStyleSheet(self._button_style(t['btn_neutral_bg'], t['btn_neutral_hover']))
        settings_btn.clicked.connect(self.settings_requested.emit)
        header.addWidget(settings_btn)

        main_layout.addLayout(header)

        # Running games indicator
        self.running_bar = QLabel("")
        self.running_bar.setStyleSheet(f"""
            background: {t['surface_alt']};
            color: {t['success']};
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 11px;
        """)
        self.running_bar.hide()
        main_layout.addWidget(self.running_bar)

        # Next check countdown
        self.countdown_label = QLabel("")
        self.countdown_label.setStyleSheet(f"color: {t['text_dim']}; font-size: 10px;")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.countdown_label)

        # Scroll area for game rows
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        self.games_layout = QVBoxLayout(scroll_widget)
        self.games_layout.setSpacing(4)
        self.games_layout.setContentsMargins(0, 0, 4, 0)
        self.games_layout.addStretch()

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll, stretch=1)

        # Bottom bar
        bottom = QHBoxLayout()
        add_btn = QPushButton("+ Add Game")
        add_btn.setFixedHeight(32)
        add_btn.setStyleSheet(self._button_style(t['btn_success_bg'], t['btn_success_hover'], text_color=t['btn_success_text']))
        add_btn.clicked.connect(self._on_add_game)
        bottom.addWidget(add_btn)
        bottom.addStretch()

        open_logs_btn = QPushButton("📁 Session Logs")
        open_logs_btn.setFixedHeight(32)
        open_logs_btn.setStyleSheet(self._button_style(t['btn_logs_bg'], t['btn_logs_hover']))
        open_logs_btn.clicked.connect(self._open_logs)
        bottom.addWidget(open_logs_btn)

        main_layout.addLayout(bottom)

        self._populate_games()

    def _populate_games(self):
        while self.games_layout.count() > 1:
            item = self.games_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        games = self.game_manager.games
        for game in games:
            if not game.get("enabled", True):
                continue
            row = GameRow(game, self.theme)
            row.report_clicked.connect(self._on_report)

            if game.get("last_ping") is not None:
                row.update_ping(game["last_ping"], game.get("ping_history", []))

            self.game_rows[game["name"]] = row
            self.games_layout.insertWidget(self.games_layout.count() - 1, row)

    def update_game_ping(self, result):
        row = self.game_rows.get(result.game_name)
        if row:
            game = next((g for g in self.game_manager.games if g["name"] == result.game_name), None)
            history = game.get("ping_history", []) if game else []
            row.update_ping(result.ms, history)

    def set_checking(self, is_checking):
        if is_checking:
            self.check_btn.setText("Checking…")
            self.check_btn.setEnabled(False)
            self.status_label.setText("Checking…")
        else:
            self.check_btn.setText("Check Now")
            self.check_btn.setEnabled(True)
            self.status_label.setText(f"Last check: {datetime.datetime.now().strftime('%H:%M:%S')}")

    def set_countdown(self, seconds_remaining):
        if seconds_remaining > 0:
            m, s = divmod(seconds_remaining, 60)
            self.countdown_label.setText(f"Next check in {m}:{s:02d}")
        else:
            self.countdown_label.setText("")

    def show_running_games(self, games):
        if games:
            names = ", ".join(games)
            self.running_bar.setText(f"▶ Running: {names}")
            self.running_bar.show()
        else:
            self.running_bar.hide()

    def _on_check_now(self):
        self.set_checking(True)
        self.check_now_requested.emit()

    def _on_add_game(self):
        dialog = AddGameDialog(self.theme, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            game_data = dialog.get_game_data()
            if game_data:
                if self.game_manager.add_game(game_data):
                    self._populate_games()
                else:
                    QMessageBox.warning(
                        self,
                        "Duplicate Game",
                        f'A game named "{game_data["name"]}" is already in your list.'
                    )

    def _on_report(self, game):
        webhook = DISCORD_REPORT_WEBHOOK
        dialog = ReportDialog(game, webhook, self.theme, self)
        dialog.exec()

    def _open_logs(self):
        from settings import LOGS_DIR
        import subprocess, sys
        try:
            if sys.platform == "win32":
                subprocess.Popen(["explorer", str(LOGS_DIR)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(LOGS_DIR)])
            else:
                subprocess.Popen(["xdg-open", str(LOGS_DIR)])
        except Exception as e:
            QMessageBox.information(self, "Logs", f"Logs are saved to:\n{LOGS_DIR}")

    def _stylesheet(self):
        t = self.theme
        return f"""
            QMainWindow, QWidget {{
                background-color: {t['bg']};
                color: {t['text']};
            }}
            QScrollBar:vertical {{
                background: {t['scrollbar_track']};
                width: 6px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {t['scrollbar_handle']};
                border-radius: 3px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """

    def _button_style(self, bg, hover_bg, text_color=None):
        if text_color is None:
            text_color = self.theme['text']
        return f"""
            QPushButton {{
                background: {bg};
                color: {text_color};
                border: none;
                border-radius: 6px;
                padding: 2px 14px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {hover_bg};
            }}
            QPushButton:pressed {{
                background: {bg};
            }}
            QPushButton:disabled {{
                color: {self.theme['text_dim']};
            }}
        """
