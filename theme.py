"""
theme.py - Central color palette for PingGuard's UI.

Every widget reads its colors from here instead of hardcoding hex values.
To add a new theme, copy one of the dicts below and adjust the values —
every key must be present in both, or widgets using the missing key will
throw a KeyError.

NOTE for StartGuard port: this module has no PingGuard-specific imports
or naming — it can be copied into StartGuard as-is and reused directly.
"""

THEMES = {
    "dark": {
        "bg": "#13131f",
        "surface": "#1e1e2e",
        "surface_alt": "#1a1a2e",
        "row_hover": "#222235",
        "surface_hover": "#262637",
        "border": "#3a3a5e",
        "border_alt": "#2a2a3e",

        "text": "#e0e0e0",
        "text_bright": "#e0e0ff",
        "text_muted": "#666680",
        "text_dim": "#444466",
        "text_faint": "#888888",
        "text_very_dim": "#555566",
        "label_secondary": "#aaaacc",

        "chart_grid": "#1e1e35",
        "chart_stats_text": "#667788",

        "accent": "#4c4cff",
        "accent_hover": "#6666ff",

        "success": "#00e676",
        "danger": "#f44336",
        "warning": "#ff9800",

        "btn_success_bg": "#1e3a1e",
        "btn_success_hover": "#2a502a",
        "btn_success_text": "#69f0ae",

        "btn_neutral_bg": "#2a2a3e",
        "btn_neutral_hover": "#3a3a5e",

        "btn_logs_bg": "#1a1a2e",
        "btn_logs_hover": "#262637",

        "report_hover_bg": "#33334a",

        "ping_excellent": "#00e676",
        "ping_good": "#69f0ae",
        "ping_fair": "#ffeb3b",
        "ping_poor": "#ff9800",
        "ping_critical": "#f44336",
        "ping_unknown": "#888888",

        "btn_report_bg": "#ff6b35",
        "btn_report_hover": "#ff8555",

        "scrollbar_track": "#1a1a2e",
        "scrollbar_handle": "#3a3a5e",
    },
    "light": {
        "bg": "#f4f5fa",
        "surface": "#ffffff",
        "surface_alt": "#eef0f7",
        "row_hover": "#f0f1fa",
        "surface_hover": "#e7e9f5",
        "border": "#d8dae6",
        "border_alt": "#e2e4ee",

        "text": "#1c1c2e",
        "text_bright": "#14143a",
        "text_muted": "#6b6b85",
        "text_dim": "#9494a8",
        "text_faint": "#8a8aa0",
        "text_very_dim": "#aaaabe",
        "label_secondary": "#5a5a78",

        "chart_grid": "#e2e4ee",
        "chart_stats_text": "#6b6b85",

        "accent": "#4c4cff",
        "accent_hover": "#3b3bdb",

        "success": "#1b8a4b",
        "danger": "#c62828",
        "warning": "#b25900",

        "btn_success_bg": "#e3f3e6",
        "btn_success_hover": "#d0ecd5",
        "btn_success_text": "#1b8a4b",

        "btn_neutral_bg": "#e9eaf2",
        "btn_neutral_hover": "#dadcec",

        "btn_logs_bg": "#eef0f7",
        "btn_logs_hover": "#e2e4f5",

        "report_hover_bg": "#e7e9f5",

        "ping_excellent": "#1b8a4b",
        "ping_good": "#558b2f",
        "ping_fair": "#a87c00",
        "ping_poor": "#b25900",
        "ping_critical": "#c62828",
        "ping_unknown": "#8a8aa0",

        "btn_report_bg": "#ff6b35",
        "btn_report_hover": "#ff8555",

        "scrollbar_track": "#e9eaf2",
        "scrollbar_handle": "#c3c5d8",
    },
}


def get_theme(name):
    """Return the theme dict for the given name, falling back to dark
    if the name is missing/invalid (e.g. a corrupted settings.json)."""
    return THEMES.get(name, THEMES["dark"])
