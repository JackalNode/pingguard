"""
setup_wizard.py - First-time setup wizard shown on first launch
"""
import re

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QWidget, QCheckBox, QScrollArea, QFrame,
    QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from games import DEFAULT_GAMES
from ping_engine import tcp_ping

# Matches names like "Overwatch 2 (EU)" -> ("Overwatch 2", "EU"). Used to
# group regional siblings together so the games checklist can pre-check
# just the one matching the user's chosen region instead of all of them.
_REGION_VARIANT_RE = re.compile(r"^(.*) \((EU|NA|Asia|SA|OCE|Africa)\)$")


def _split_region_variant(name):
    match = _REGION_VARIANT_RE.match(name)
    if match:
        return match.group(1), match.group(2)
    return name, None


class RegionLatencyWorker(QThread):
    """
    TCP latency test against one representative AWS region endpoint per
    geographic region.

    AWS regional endpoints map to real, fixed datacenters rather than
    anycast/CDN-fronted infrastructure - confirmed by direct testing
    from South Africa, which returned genuinely distinguishing numbers
    (Africa 24ms, EU 172ms, NA 207ms, SA 143ms, Asia 312ms, OCE 369ms)
    instead of the suspiciously-flat numbers the original Battle.net
    hostnames gave everywhere.
    """
    finished_testing = pyqtSignal(dict)  # value -> ms_or_None

    REGION_TARGETS = [
        ("🌍  Europe", "EU", "ec2.eu-west-1.amazonaws.com"),
        ("🌎  North America", "NA", "ec2.us-east-1.amazonaws.com"),
        ("🌏  Asia Pacific", "Asia", "ec2.ap-southeast-1.amazonaws.com"),
        ("🌎  South America", "SA", "ec2.sa-east-1.amazonaws.com"),
        ("🌏  Oceania", "OCE", "ec2.ap-southeast-2.amazonaws.com"),
        ("🌍  Africa", "Africa", "ec2.af-south-1.amazonaws.com"),
    ]

    def run(self):
        results = {}
        for _, value, host in self.REGION_TARGETS:
            try:
                ms, success, _ = tcp_ping(host, 443, timeout=3.0)
                results[value] = ms if success else None
            except Exception:
                results[value] = None
        self.finished_testing.emit(results)


class SetupWizard(QDialog):
    def __init__(self, settings, game_manager, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.game_manager = game_manager
        self.setWindowTitle("Welcome to PingGuard")
        self.setModal(True)
        self.setFixedSize(500, 520)
        self.setStyleSheet("""
            QDialog { background: #13131f; color: #e0e0e0; }
            QLabel { color: #e0e0e0; }
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, stretch=1)

        self.stack.addWidget(self._page_welcome())
        self._region_page_index = self.stack.addWidget(self._page_region())
        self._games_page_index = self.stack.addWidget(self._page_games())
        self.stack.addWidget(self._page_ready())
        self.stack.currentChanged.connect(self._on_page_changed)

        # Navigation bar
        nav = QWidget()
        nav.setStyleSheet("background: #0d0d1a; border-top: 1px solid #2a2a3e;")
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(20, 14, 20, 14)

        self.back_btn = QPushButton("← Back")
        self.back_btn.setFixedHeight(36)
        self.back_btn.setStyleSheet("""
            QPushButton { background: #1e1e2e; color: #888888; border: 1px solid #2a2a3e;
                          border-radius: 6px; padding: 4px 16px; }
            QPushButton:hover { color: #e0e0e0; background: #262637; }
        """)
        self.back_btn.clicked.connect(self._go_back)
        self.back_btn.hide()

        self.step_label = QLabel("Step 1 of 4")
        self.step_label.setStyleSheet("color: #444466; font-size: 11px;")
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.next_btn = QPushButton("Next →")
        self.next_btn.setFixedHeight(36)
        self.next_btn.setStyleSheet("""
            QPushButton { background: #4c4cff; color: white; border: none;
                          border-radius: 6px; padding: 4px 20px; font-weight: bold; }
            QPushButton:hover { background: #6666ff; }
        """)
        self.next_btn.clicked.connect(self._go_next)

        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.step_label)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)

        layout.addWidget(nav)

    def _page_welcome(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 30)
        layout.setSpacing(16)

        emoji = QLabel("🎮")
        emoji.setFont(QFont("Segoe UI Emoji", 48))
        emoji.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(emoji)

        title = QLabel("Welcome to PingGuard")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #e0e0ff;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(
            "PingGuard monitors your connection to game servers\n"
            "and alerts you when your ping spikes or drops out —\n"
            "so you know if it's you or the servers."
        )
        desc.setStyleSheet("color: #888899; font-size: 13px; line-height: 1.6;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

        features = QLabel("✓  Real ping testing, not fake ICMP\n✓  Runs quietly in your system tray\n✓  Alerts before you queue into a laggy game")
        features.setStyleSheet("color: #666680; font-size: 12px; line-height: 1.8;")
        features.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(features)

        layout.addStretch()
        return page

    def _page_games(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 12)
        layout.setSpacing(10)

        title = QLabel("Which games do you play?")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #e0e0ff;")
        layout.addWidget(title)

        subtitle = QLabel("PingGuard will monitor these. You can change this later.")
        subtitle.setStyleSheet("color: #666680; font-size: 11px;")
        layout.addWidget(subtitle)

        # Select all
        sel_row = QHBoxLayout()
        sel_all = QPushButton("Select All")
        sel_all.setFixedHeight(28)
        sel_all.setStyleSheet("""
            QPushButton { background: transparent; color: #4c4cff; border: none; font-size: 11px; }
            QPushButton:hover { color: #8888ff; }
        """)
        sel_none = QPushButton("Select None")
        sel_none.setFixedHeight(28)
        sel_none.setStyleSheet(sel_all.styleSheet())

        sel_row.addWidget(sel_all)
        sel_row.addWidget(sel_none)
        sel_row.addStretch()
        layout.addLayout(sel_row)

        # Scrollable game list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(4)
        scroll_layout.setContentsMargins(0, 0, 4, 0)

        self.game_checks = {}
        for game in DEFAULT_GAMES:
            cb = QCheckBox(f"  {game['name']}  -  {game.get('category','')}")
            cb.setChecked(True)
            cb.setTristate(False)
            cb.setStyleSheet("""
                QCheckBox { color: #ccccdd; font-size: 12px; padding: 5px 4px; }
                QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px;
                    background: #1e1e2e; border: 2px solid #3a3a5e; }
                QCheckBox::indicator:checked { background: #4c4cff; border-color: #6666ff; }
                QCheckBox::indicator:unchecked { background: #1e1e2e; border-color: #3a3a5e; }
            """)
            self.game_checks[game["name"]] = cb
            scroll_layout.addWidget(cb)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, stretch=1)

        sel_all.clicked.connect(lambda: [cb.setChecked(True) for cb in self.game_checks.values()])
        sel_none.clicked.connect(lambda: [cb.setChecked(False) for cb in self.game_checks.values()])

        return page

    def _get_selected_region(self):
        for value, (radio, _) in self.region_rows.items():
            if radio.isChecked():
                return value
        return None

    def _on_page_changed(self, index):
        if index == self._games_page_index:
            self._apply_region_aware_checks()

    def _apply_region_aware_checks(self):
        """
        Re-applies which game checkboxes start checked, based on the
        region chosen on the previous wizard page.

        Without this, every regional variant of a game (e.g. both
        "Overwatch 2 (EU)" and "Overwatch 2 (NA)") defaults to checked
        together, defeating the entire point of separating them - a
        fresh install would end up monitoring every region of a game
        at once instead of just the one the user actually plays on.
        """
        selected_region = self._get_selected_region()

        groups = {}
        for game in DEFAULT_GAMES:
            base, region = _split_region_variant(game["name"])
            groups.setdefault(base, []).append((game["name"], region))

        for base, entries in groups.items():
            regions_in_group = [region for _, region in entries if region is not None]
            if not regions_in_group:
                continue  # not a regional game - leave its checkbox alone

            if selected_region in regions_in_group:
                # A variant matches the chosen region - check only that one.
                for name, region in entries:
                    cb = self.game_checks.get(name)
                    if cb is not None:
                        cb.setChecked(region == selected_region)
            else:
                # No variant covers the chosen region yet - show every
                # option rather than silently hiding all of them.
                for name, _ in entries:
                    cb = self.game_checks.get(name)
                    if cb is not None:
                        cb.setChecked(True)

    def _page_region(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 20)
        layout.setSpacing(12)

        title = QLabel("Where are you located?")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #e0e0ff;")
        layout.addWidget(title)

        desc = QLabel(
            "This sets a sensible starting default. You can still pick a\n"
            "different server for any individual game later — for example,\n"
            "playing League on EU but Counter-Strike on a local server."
        )
        desc.setStyleSheet("color: #666680; font-size: 11px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(12)

        self.region_rows = {}
        self.region_button_group = QButtonGroup(page)

        for label, value, _host in RegionLatencyWorker.REGION_TARGETS:
            row = QHBoxLayout()
            radio = QRadioButton(label)
            radio.setStyleSheet("""
                QRadioButton { color: #e0e0e0; font-size: 13px; padding: 6px 0; }
                QRadioButton::indicator { width: 16px; height: 16px; }
            """)
            ms_label = QLabel("Testing...")
            ms_label.setStyleSheet("color: #666680; font-size: 12px;")
            ms_label.setFixedWidth(80)
            ms_label.setAlignment(Qt.AlignmentFlag.AlignRight)

            self.region_button_group.addButton(radio)
            row.addWidget(radio)
            row.addStretch()
            row.addWidget(ms_label)
            layout.addLayout(row)

            self.region_rows[value] = (radio, ms_label)

        self.region_test_label = QLabel("Testing your connection to each region...")
        self.region_test_label.setStyleSheet("color: #4c4cff; font-size: 11px;")
        self.region_test_label.setWordWrap(True)
        layout.addSpacing(8)
        layout.addWidget(self.region_test_label)

        layout.addStretch()

        note = QLabel("ℹ This can be changed in Settings at any time.")
        note.setStyleSheet("color: #444466; font-size: 11px;")
        layout.addWidget(note)

        self._start_region_latency_test()

        return page

    def _start_region_latency_test(self):
        self._region_latency_thread = RegionLatencyWorker(self)
        self._region_latency_thread.finished_testing.connect(self._on_region_latency_done)
        self._region_latency_thread.start()

    def _on_region_latency_done(self, results):
        fastest_value = None
        fastest_ms = None

        for _, value, _host in RegionLatencyWorker.REGION_TARGETS:
            ms = results.get(value)
            _, ms_label = self.region_rows[value]
            if ms is not None:
                ms_label.setText(f"{ms}ms")
                if fastest_ms is None or ms < fastest_ms:
                    fastest_ms = ms
                    fastest_value = value
            else:
                ms_label.setText("Unavailable")

        if fastest_value is not None:
            radio, _ = self.region_rows[fastest_value]
            radio.setChecked(True)
            self.region_test_label.setText(
                "✓ Pre-selected the fastest as a starting point — pick any other if you'd rather."
            )
        else:
            self.region_test_label.setText(
                "Couldn't test automatically — pick whichever matches where you play."
            )

    def _page_ready(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 30)
        layout.setSpacing(16)

        emoji = QLabel("🚀")
        emoji.setFont(QFont("Segoe UI Emoji", 48))
        emoji.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(emoji)

        title = QLabel("You're all set!")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #e0e0ff;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(
            "PingGuard will now run in your system tray.\n"
            "Right-click the tray icon to open, check ping, or quit.\n\n"
            "Click 'Start PingGuard' to run your first ping check!"
        )
        desc.setStyleSheet("color: #888899; font-size: 13px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()
        return page

    def _go_next(self):
        idx = self.stack.currentIndex()
        if idx == self.stack.count() - 1:
            self._finish()
            return

        self.stack.setCurrentIndex(idx + 1)
        self._update_nav()

    def _go_back(self):
        idx = self.stack.currentIndex()
        if idx > 0:
            self.stack.setCurrentIndex(idx - 1)
        self._update_nav()

    def _update_nav(self):
        idx = self.stack.currentIndex()
        total = self.stack.count()
        self.step_label.setText(f"Step {idx + 1} of {total}")
        self.back_btn.setVisible(idx > 0)
        self.next_btn.setText("Start PingGuard 🚀" if idx == total - 1 else "Next →")

    def _finish(self):
        # Save game selections
        for game in self.game_manager.games:
            checked = self.game_checks.get(game["name"])
            if checked is not None:
                game["enabled"] = checked.isChecked()
        self.game_manager.save()

        # Save region
        self.settings.set("user_region", self._get_selected_region() or "EU")
        self.settings.set("first_run", False)

        self.accept()
