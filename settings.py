"""
settings.py - Persistent settings and game config storage
Uses JSON files in the user's AppData/config directory
"""
import json
import os
import sys
from pathlib import Path
from games import DEFAULT_GAMES


def get_data_dir():
    """Get the platform-appropriate data directory."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home())
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
    
    data_dir = Path(base) / "PingGuard"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


DATA_DIR = get_data_dir()
SETTINGS_FILE = DATA_DIR / "settings.json"
GAMES_FILE = DATA_DIR / "games.json"
LOGS_DIR = DATA_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)
(DATA_DIR / "assets").mkdir(exist_ok=True)
(DATA_DIR / "data").mkdir(exist_ok=True)


DEFAULT_SETTINGS = {
    "first_run": True,
    "auto_check_interval": 120,       # seconds
    "sound_enabled": True,
    "notifications_enabled": True,
    "start_minimized": True,
    "start_with_windows": False,
    "alert_threshold_ms": 150,         # alert if ping goes above this
    # discord_webhook removed — lives in constants.py only, never in settings
    "user_region": "EU",
    "check_on_game_launch": True,
    "theme": "dark",
    "version": "2.0.4",
}


class Settings:
    def __init__(self):
        self._data = {}
        self.load()

    def load(self):
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r") as f:
                    saved = json.load(f)
                # Merge with defaults (adds new keys from updates)
                # Also strip out any old discord_webhook that may exist in a
                # user's saved settings.json from a previous install
                saved.pop("discord_webhook", None)
                self._data = {**DEFAULT_SETTINGS, **saved}
            except Exception:
                self._data = DEFAULT_SETTINGS.copy()
        else:
            self._data = DEFAULT_SETTINGS.copy()

    def save(self):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(self._data, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self.save()

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self.set(key, value)


def migrate_game_endpoints(games_list):
    """Update endpoints for games that had bad defaults."""
    fixes = {
        'CS2': {
            'endpoints': [
                {'host': 'steamcommunity.com', 'port': 443},
                {'host': 'api.steampowered.com', 'port': 443},
            ],
            'region_note': 'Steam servers',
            'is_stale': lambda hosts: any(h.startswith('185.') or h.startswith('146.') for h in hosts),
        },
        'Dota 2': {
            'endpoints': [
                {'host': 'steamcommunity.com', 'port': 443},
                {'host': 'api.steampowered.com', 'port': 443},
            ],
            'region_note': 'Steam servers',
            'is_stale': lambda hosts: any(h.startswith('185.') or h.startswith('146.') for h in hosts),
        },
        'Call of Duty: Warzone': {
            'endpoints': [
                {'host': 'eu.battle.net', 'port': 443},
                {'host': '185.34.106.103', 'port': 3074},
            ],
            'region_note': 'EU servers',
            'is_stale': lambda hosts: '172.64.155.188' in hosts,
        },
        'Apex Legends': {
            'endpoints': [
                {'host': '100.50.20.250', 'port': 9000},
            ],
            'region_note': 'EA servers (US-East, AWS)',
            'is_stale': lambda hosts: 'eaassets-a.akamaihd.net' in hosts or '159.153.64.1' in hosts,
        },
        'Path of Exile': {
            'endpoints': [
                {'host': '34.144.246.52', 'port': 6112},
            ],
            'region_note': 'South Africa servers (Google Cloud)',
            'exe': ['PathOfExile.exe', 'PathOfExileSteam.exe'],
            'is_stale': lambda hosts: 'www.pathofexile.com' in hosts or '45.33.26.109' in hosts,
        },
    }
    changed = False
    for game in games_list:
        if game['name'] not in fixes:
            continue
        fix = fixes[game['name']]
        current_hosts = [e['host'] for e in game.get('endpoints', [])]
        if fix['is_stale'](current_hosts):
            game['endpoints'] = fix['endpoints']
            game['region_note'] = fix['region_note']
            if 'exe' in fix:
                game['exe'] = fix['exe']
            changed = True
    return changed

def migrate_game_regions(games_list):
    """
    Some games used to ship as a single blended entry covering multiple
    regions (e.g. one "Overwatch 2" entry that tried EU first, then
    fell back to NA). Because a TCP connection that gets actively
    refused still counts as a successful ping in ping_engine.py (the
    server is reachable, just saying no) - the fallback endpoint never
    actually got used in practice. Non-EU players were unknowingly
    having their EU latency reported as their ping.

    This splits each affected game into separate, standalone region
    entries - one per region - the same way every other game in this
    list already works. The original entry's saved ping_history,
    enabled state, and last_ping are preserved by renaming it in place
    to become its first region. Any brand-new region variant is added
    fresh and disabled by default - nothing should start monitoring or
    alerting on a region the user never chose for themselves.
    """
    # old_name -> ordered list of (new_name, endpoint, region_note).
    # The first entry in each list is what the existing saved entry
    # gets renamed to; everything after that is added as a new,
    # disabled entry.
    splits = {
        "Overwatch 2": [
            ("Overwatch 2 (EU)", {"host": "eu.battle.net", "port": 443}, "Battle.net EU"),
            ("Overwatch 2 (NA)", {"host": "us.battle.net", "port": 443}, "Battle.net NA"),
        ],
    }

    changed = False
    existing_names = {g["name"] for g in games_list}

    for old_name, variants in splits.items():
        if old_name not in existing_names:
            continue  # already migrated on a previous run, or never existed for this user

        first_name, first_endpoint, first_region_note = variants[0]

        for game in games_list:
            if game["name"] == old_name:
                game["name"] = first_name
                game["endpoints"] = [first_endpoint]
                game["region_note"] = first_region_note
                changed = True
                break

        template = next((g for g in games_list if g["name"] == first_name), None)
        if template is None:
            continue  # shouldn't happen, but never crash a migration over it

        for new_name, endpoint, region_note in variants[1:]:
            if new_name in existing_names:
                continue
            new_game = dict(template)
            new_game["name"] = new_name
            new_game["endpoints"] = [endpoint]
            new_game["region_note"] = region_note
            new_game["enabled"] = False
            new_game["last_ping"] = None
            new_game["last_checked"] = None
            new_game["ping_history"] = []
            games_list.append(new_game)
            changed = True

    return changed


class GameManager:
    def __init__(self):
        self._games = []
        self.load()

    def load(self):
        if GAMES_FILE.exists():
            try:
                with open(GAMES_FILE, "r") as f:
                    self._games = json.load(f)
                changed = migrate_game_endpoints(self._games)
                if migrate_game_regions(self._games):
                    changed = True
                if changed:
                    self.save()
            except Exception:
                self._reset_to_defaults()
        else:
            self._reset_to_defaults()

    def _reset_to_defaults(self):
        """Load default games with enabled=True and empty history."""
        self._games = []
        for g in DEFAULT_GAMES:
            game = dict(g)
            game["enabled"] = True
            game["last_ping"] = None
            game["last_checked"] = None
            game["ping_history"] = []   # list of {ts, ms} dicts
            self._games.append(game)
        self.save()

    def save(self):
        try:
            with open(GAMES_FILE, "w") as f:
                json.dump(self._games, f, indent=2)
        except Exception as e:
            print(f"Failed to save games: {e}")

    @property
    def games(self):
        return self._games

    def get_enabled(self):
        return [g for g in self._games if g.get("enabled", True)]

    def update_ping(self, game_name, ping_ms, timestamp):
        for game in self._games:
            if game["name"] == game_name:
                game["last_ping"] = ping_ms
                game["last_checked"] = timestamp
                # Keep last 60 readings (2hrs at 2min intervals)
                history = game.get("ping_history", [])
                history.append({"ts": timestamp, "ms": ping_ms})
                game["ping_history"] = history[-60:]
                break
        self.save()

    def add_game(self, game_dict):
        name = game_dict.get("name", "")
        if any(g["name"].lower() == name.lower() for g in self._games):
            return False
        game_dict["enabled"] = True
        game_dict["last_ping"] = None
        game_dict["last_checked"] = None
        game_dict["ping_history"] = []
        self._games.append(game_dict)
        self.save()
        return True

    def remove_game(self, game_name):
        self._games = [g for g in self._games if g["name"] != game_name]
        self.save()

    def update_game(self, game_name, updates):
        for game in self._games:
            if game["name"] == game_name:
                game.update(updates)
                break
        self.save()
