"""
game_detector.py

Scans the local PC for installed games across supported launchers
(Steam, Epic Games, Riot Client, Battle.net) so the user can pick
their game from a dropdown in Add Game instead of typing everything
in by hand.

Design rule: every detector function below is fully independent and
self-contained. If a launcher isn't installed, or its files are
missing / corrupted / in an unexpected format, that detector quietly
returns an empty list rather than raising an exception. One broken or
missing launcher must never take down the others, and must never
crash the Add Game dialog.

No third-party dependencies - everything here uses only Python's
standard library (winreg, json, os, re).
"""

import json
import os
import re
import winreg


class DetectedGame:
    """Plain data holder for one detected installed game."""

    def __init__(self, name, source, install_path=None):
        self.name = name
        self.source = source  # "Steam", "Epic", "Riot", "Battle.net"
        self.install_path = install_path

    def __repr__(self):
        return f"DetectedGame(name={self.name!r}, source={self.source!r})"


# ---------------------------------------------------------------------------
# Steam
# ---------------------------------------------------------------------------

def _get_steam_install_path():
    """Find where Steam itself is installed, via the registry."""
    registry_locations = [
        (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", "InstallPath"),
    ]
    for hive, path, value_name in registry_locations:
        try:
            with winreg.OpenKey(hive, path) as key:
                value, _ = winreg.QueryValueEx(key, value_name)
                if value and os.path.isdir(value):
                    return value
        except OSError:
            continue
    return None


def _parse_library_folders_vdf(vdf_path):
    """
    Steam's libraryfolders.vdf lists every drive/folder where the user
    has a Steam library. It's Valve's own text format (not JSON), but
    the part we need - quoted "path" values - is simple enough to pull
    out with a regex rather than pulling in a third-party VDF parser.
    """
    library_paths = []
    try:
        with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        # Matches lines like:   "path"        "D:\\SteamLibrary"
        for match in re.finditer(r'"path"\s*"([^"]+)"', content):
            raw_path = match.group(1).replace("\\\\", "\\")
            if os.path.isdir(raw_path):
                library_paths.append(raw_path)
    except OSError:
        pass
    return library_paths


def _parse_app_manifest(acf_path):
    """Pull the game name and installdir out of one appmanifest_*.acf file."""
    try:
        with open(acf_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        name_match = re.search(r'"name"\s*"([^"]+)"', content)
        installdir_match = re.search(r'"installdir"\s*"([^"]+)"', content)
        if name_match:
            return name_match.group(1), (installdir_match.group(1) if installdir_match else None)
    except OSError:
        pass
    return None, None


def detect_steam_games():
    games = []
    try:
        steam_path = _get_steam_install_path()
        if not steam_path:
            return games

        steamapps_path = os.path.join(steam_path, "steamapps")
        libraryfolders_vdf = os.path.join(steamapps_path, "libraryfolders.vdf")

        # Steam's own install folder always counts as a library too.
        library_roots = [steamapps_path]
        if os.path.isfile(libraryfolders_vdf):
            for lib_path in _parse_library_folders_vdf(libraryfolders_vdf):
                lib_steamapps = os.path.join(lib_path, "steamapps")
                if os.path.isdir(lib_steamapps) and lib_steamapps not in library_roots:
                    library_roots.append(lib_steamapps)

        for steamapps_dir in library_roots:
            try:
                for filename in os.listdir(steamapps_dir):
                    if filename.startswith("appmanifest_") and filename.endswith(".acf"):
                        acf_path = os.path.join(steamapps_dir, filename)
                        name, installdir = _parse_app_manifest(acf_path)
                        if name:
                            install_path = (
                                os.path.join(steamapps_dir, "common", installdir)
                                if installdir else None
                            )
                            if install_path is None or os.path.isdir(install_path):
                                games.append(DetectedGame(name, "Steam", install_path))
            except OSError:
                continue
    except Exception:
        # Belt-and-braces: a Steam detection failure should never take
        # down the whole scan.
        pass
    return games


# ---------------------------------------------------------------------------
# Epic Games
# ---------------------------------------------------------------------------

def detect_epic_games():
    games = []
    manifests_dir = r"C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests"
    try:
        if not os.path.isdir(manifests_dir):
            return games
        for filename in os.listdir(manifests_dir):
            if not filename.endswith(".item"):
                continue
            item_path = os.path.join(manifests_dir, filename)
            try:
                with open(item_path, "r", encoding="utf-8", errors="ignore") as f:
                    data = json.load(f)
                name = data.get("DisplayName")
                install_path = data.get("InstallLocation")
                if name and (not install_path or os.path.isdir(install_path)):
                    games.append(DetectedGame(name, "Epic", install_path))
            except (OSError, json.JSONDecodeError):
                continue
    except Exception:
        pass
    return games


# ---------------------------------------------------------------------------
# Riot Games (League of Legends, Valorant, etc.)
# ---------------------------------------------------------------------------

# Riot's internal product codes don't read well as display names -
# translate the ones we know about. Anything unrecognised falls back
# to a cleaned-up version of the raw code so it still shows up in the
# dropdown rather than vanishing silently.
_RIOT_PRODUCT_NAMES = {
    "league_of_legends.live": "League of Legends",
    "valorant.live": "VALORANT",
    "lor.live": "Legends of Runeterra",
}


def detect_riot_games():
    games = []
    installs_path = r"C:\ProgramData\Riot Games\RiotClientInstalls.json"
    try:
        if not os.path.isfile(installs_path):
            return games
        with open(installs_path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
        # Top-level keys are Riot's internal product codes, each
        # mapped to its install path on disk.
        for product_code, install_path in data.items():
            if not isinstance(install_path, str) or not os.path.isdir(install_path):
                continue
            display_name = _RIOT_PRODUCT_NAMES.get(
                product_code,
                product_code.replace(".live", "").replace("_", " ").title(),
            )
            games.append(DetectedGame(display_name, "Riot", install_path))
    except (OSError, json.JSONDecodeError):
        pass
    except Exception:
        pass
    return games


# ---------------------------------------------------------------------------
# Battle.net
# ---------------------------------------------------------------------------

# Known publishers for games distributed through Battle.net. Blizzard's
# own titles (Overwatch, WoW, Diablo, Hearthstone, StarCraft) publish
# as "Blizzard Entertainment" - Activision titles (Call of Duty) run
# through Battle.net too but publish under the Activision name, so both
# need to be on this list or CoD silently never shows up.
_BATTLENET_PUBLISHERS = {
    "blizzard entertainment",
    "activision",
    "activision blizzard",
    "activision publishing, inc.",
}


def _safe_registry_value(key, value_name):
    try:
        value, _ = winreg.QueryValueEx(key, value_name)
        return value
    except OSError:
        return None


def detect_battlenet_games():
    """
    Reads installed Battle.net games from the Windows uninstall registry
    keys rather than Battle.net's own internal database (product.db),
    which is a binary protobuf file that's fragile to parse and can
    change between Battle.net client updates.

    Known limitation: a game Battle.net shows as "ready to install" but
    has never actually been fully installed/repaired won't have a
    registry entry yet, so it won't appear here. Acceptable gap for v1 -
    only revisit if it turns out to affect real users.
    """
    games = []
    uninstall_roots = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    seen_names = set()
    try:
        for hive, root_path in uninstall_roots:
            try:
                with winreg.OpenKey(hive, root_path) as root_key:
                    subkey_count = winreg.QueryInfoKey(root_key)[0]
                    for i in range(subkey_count):
                        try:
                            subkey_name = winreg.EnumKey(root_key, i)
                            with winreg.OpenKey(root_key, subkey_name) as subkey:
                                publisher = _safe_registry_value(subkey, "Publisher")
                                if not publisher or publisher.strip().lower() not in _BATTLENET_PUBLISHERS:
                                    continue
                                name = _safe_registry_value(subkey, "DisplayName")
                                install_path = _safe_registry_value(subkey, "InstallLocation")
                                if name and name not in seen_names:
                                    if not install_path or os.path.isdir(install_path):
                                        seen_names.add(name)
                                        games.append(
                                            DetectedGame(name, "Battle.net", install_path or None)
                                        )
                        except OSError:
                            continue
            except OSError:
                continue
    except Exception:
        pass
    return games


# ---------------------------------------------------------------------------
# Combined entry point
# ---------------------------------------------------------------------------

def detect_all_games():
    """
    Runs every detector and returns one merged, de-duplicated,
    alphabetically-sorted list of DetectedGame objects.

    Safe to call even if every launcher above is missing from this PC -
    in that case this simply returns an empty list, and the Add Game
    dialog falls back to its manual-entry option.

    This does several disk reads and registry calls, so the caller
    should run it off the main UI thread (e.g. in a QThread/worker)
    so opening Add Game doesn't freeze the window while it scans.
    """
    all_games = []
    all_games.extend(detect_steam_games())
    all_games.extend(detect_epic_games())
    all_games.extend(detect_riot_games())
    all_games.extend(detect_battlenet_games())

    # De-dupe by name (case-insensitive). Keeps whichever source was
    # found first - fine here since these four launchers don't
    # normally carry the same title.
    deduped = {}
    for game in all_games:
        key = game.name.strip().lower()
        if key not in deduped:
            deduped[key] = game

    return sorted(deduped.values(), key=lambda g: g.name.lower())
