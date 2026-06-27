"""
games.py - Pre-loaded game definitions with TCP ping endpoints
Each game has multiple endpoint options to try, since many servers block ICMP.

Process names per platform:
  exe       = Windows (.exe)
  exe_mac   = macOS (inside .app bundle, as seen by psutil)
  exe_linux = Linux (native or Proton)

Any of exe / exe_mac / exe_linux can be either a single string or a list
of strings. Use a list when a publisher has renamed the exe between
versions (see Apex Legends below) — this lets old and new installs both
still be detected, instead of overwriting one stale name with another.
"""

DEFAULT_GAMES = [
    # FPS / Shooters
    {
        "name": "Valorant",
        "exe": "VALORANT-Win64-Shipping.exe",
        "exe_mac": "VALORANT-Win64-Shipping",
        "exe_linux": "VALORANT-Win64-Shipping",
        "icon": "🎯",
        "category": "FPS",
        "endpoints": [
            {"host": "euw1.pvp.net", "port": 443},
            {"host": "eu.api.riotgames.com", "port": 443},
        ],
        "region_note": "EU West"
    },
    {
        "name": "CS2",
        "exe": "cs2.exe",
        "exe_mac": "cs2",
        "exe_linux": "cs2",
        "icon": "🔫",
        "category": "FPS",
        "endpoints": [
            {"host": "steamcommunity.com", "port": 443},
            {"host": "api.steampowered.com", "port": 443},
        ],
        "region_note": "Steam servers"
    },
    {
        "name": "Apex Legends",
        "exe": ["r5apex.exe", "r5apex_dx12.exe"],
        "exe_mac": "r5apex",
        "exe_linux": "r5apex",
        "icon": "🦅",
        "category": "FPS",
        "endpoints": [
            {"host": "100.50.20.250", "port": 9000},
        ],
        "region_note": "EA servers (US-East, AWS)"
    },
    {
        "name": "Overwatch 2 (EU)",
        "exe": "Overwatch.exe",
        "exe_mac": "Overwatch",
        "exe_linux": "Overwatch",
        "icon": "⚡",
        "category": "FPS",
        "endpoints": [
            {"host": "eu.battle.net", "port": 443},
        ],
        "region_note": "Battle.net EU"
    },
    {
        "name": "Overwatch 2 (NA)",
        "exe": "Overwatch.exe",
        "exe_mac": "Overwatch",
        "exe_linux": "Overwatch",
        "icon": "⚡",
        "category": "FPS",
        "endpoints": [
            {"host": "us.battle.net", "port": 443},
        ],
        "region_note": "Battle.net NA"
    },
    {
        "name": "Call of Duty: Warzone",
        "exe": "cod.exe",
        "exe_mac": "cod",
        "exe_linux": "cod",
        "icon": "💥",
        "category": "FPS",
        "endpoints": [
            {"host": "eu.battle.net", "port": 443},
            {"host": "185.34.106.103", "port": 3074},
        ],
        "region_note": "EU servers"
    },

    # Battle Royale
    {
        "name": "Fortnite",
        "exe": "FortniteClient-Win64-Shipping.exe",
        "exe_mac": "FortniteClient-Mac-Shipping",
        "exe_linux": "FortniteClient-Win64-Shipping",
        "icon": "🏗️",
        "category": "Battle Royale",
        "endpoints": [
            {"host": "account-public-service-prod.ol.epicgames.com", "port": 443},
            {"host": "fortnite-public-service-prod11.ol.epicgames.com", "port": 443},
        ],
        "region_note": "Epic EU"
    },
    {
        "name": "PUBG",
        "exe": "TslGame.exe",
        "exe_mac": "TslGame",
        "exe_linux": "TslGame",
        "icon": "🪖",
        "category": "Battle Royale",
        "endpoints": [
            {"host": "prod-live-front.playbattlegrounds.com", "port": 443},
        ],
        "region_note": "EU servers"
    },

    # MMO / RPG
    {
        "name": "World of Warcraft",
        "exe": "Wow.exe",
        "exe_mac": "World of Warcraft",
        "exe_linux": "Wow",
        "icon": "⚔️",
        "category": "MMO",
        "endpoints": [
            {"host": "eu.battle.net", "port": 443},
            {"host": "eu.actual.battle.net", "port": 1119},
        ],
        "region_note": "EU servers"
    },
    {
        "name": "Final Fantasy XIV",
        "exe": "ffxiv_dx11.exe",
        "exe_mac": "ffxiv_dx11",
        "exe_linux": "ffxiv_dx11",
        "icon": "🌙",
        "category": "MMO",
        "endpoints": [
            {"host": "frontier.ffxiv.com", "port": 443},
            {"host": "patch-bootver.ffxiv.com", "port": 443},
        ],
        "region_note": "EU Chaos DC"
    },
    {
        "name": "Path of Exile",
        "exe": ["PathOfExile.exe", "PathOfExileSteam.exe"],
        "exe_mac": "PathOfExile",
        "exe_linux": "PathOfExile",
        "icon": "💀",
        "category": "ARPG",
        "endpoints": [
            {"host": "34.144.246.52", "port": 6112},
        ],
        "region_note": "South Africa servers (Google Cloud)"
    },
    {
        "name": "Diablo IV",
        "exe": "Diablo IV.exe",
        "exe_mac": "Diablo IV",
        "exe_linux": "diablo4",
        "icon": "🔥",
        "category": "ARPG",
        "endpoints": [
            {"host": "eu.battle.net", "port": 443},
        ],
        "region_note": "Battle.net EU"
    },

    # MOBA
    {
        "name": "League of Legends",
        "exe": "League of Legends.exe",
        "exe_mac": "League of Legends",
        "exe_linux": "LeagueOfLegends",
        "icon": "🏆",
        "category": "MOBA",
        "endpoints": [
            {"host": "euw1.api.riotgames.com", "port": 443},
            {"host": "eu.api.riotgames.com", "port": 443},
        ],
        "region_note": "EUW"
    },
    {
        "name": "Dota 2",
        "exe": "dota2.exe",
        "exe_mac": "dota2",
        "exe_linux": "dota2",
        "icon": "🛡️",
        "category": "MOBA",
        "endpoints": [
            {"host": "steamcommunity.com", "port": 443},
            {"host": "api.steampowered.com", "port": 443},
        ],
        "region_note": "Steam servers"
    },

    # Sports / Racing
    {
        "name": "FIFA / EA FC",
        "exe": "FC25.exe",
        "exe_mac": "FC25",
        "exe_linux": "FC25",
        "icon": "⚽",
        "category": "Sports",
        "endpoints": [
            {"host": "ea.com", "port": 443},
            {"host": "api2.ea.com", "port": 443},
        ],
        "region_note": "EA servers"
    },
    {
        "name": "Rocket League",
        "exe": "RocketLeague.exe",
        "exe_mac": "RocketLeague",
        "exe_linux": "RocketLeague",
        "icon": "🚀",
        "category": "Sports",
        "endpoints": [
            {"host": "api.epicgames.dev", "port": 443},
            {"host": "account-public-service-prod.ol.epicgames.com", "port": 443},
        ],
        "region_note": "Epic EU"
    },

    # Other
    {
        "name": "Minecraft",
        "exe": "javaw.exe",
        "exe_mac": "java",
        "exe_linux": "java",
        "icon": "⛏️",
        "category": "Sandbox",
        "endpoints": [
            {"host": "session.minecraft.net", "port": 443},
            {"host": "api.minecraftservices.com", "port": 443},
        ],
        "region_note": "Mojang servers"
    },
    {
        "name": "GTA Online",
        "exe": "GTA5.exe",
        "exe_mac": "GTA5",
        "exe_linux": "GTA5",
        "icon": "🚗",
        "category": "Open World",
        "endpoints": [
            {"host": "prod.cloud.rockstargames.com", "port": 443},
        ],
        "region_note": "Rockstar EU"
    },
    {
        "name": "Rainbow Six Siege",
        "exe": "RainbowSix.exe",
        "exe_mac": "RainbowSix",
        "exe_linux": "RainbowSix",
        "icon": "🪟",
        "category": "FPS",
        "endpoints": [
            {"host": "uplaypc-s-ubisoft.cdn.ubi.com", "port": 443},
            {"host": "public-ubiservices.ubi.com", "port": 443},
        ],
        "region_note": "Ubisoft EU"
    },
    {
        "name": "Destiny 2",
        "exe": "destiny2.exe",
        "exe_mac": "destiny2",
        "exe_linux": "destiny2",
        "icon": "🌌",
        "category": "FPS",
        "endpoints": [
            {"host": "www.bungie.net", "port": 443},
        ],
        "region_note": "Bungie servers"
    },
    {
        "name": "Lost Ark",
        "exe": "LOSTARK.exe",
        "exe_mac": "LOSTARK",
        "exe_linux": "LOSTARK",
        "icon": "🗺️",
        "category": "ARPG",
        "endpoints": [
            {"host": "api.amazon.com", "port": 443},
        ],
        "region_note": "Amazon EU"
    },
]

# Ping quality thresholds (ms)
PING_THRESHOLDS = {
    "excellent": 30,
    "good": 60,
    "fair": 100,
    "poor": 150,
    # above 150 = critical
}

_DEFAULT_PING_COLORS = {
    "unknown": "#888888",
    "excellent": "#00e676",
    "good": "#69f0ae",
    "fair": "#ffeb3b",
    "poor": "#ff9800",
    "critical": "#f44336",
}

_PING_THEME_KEY = {
    "unknown": "ping_unknown",
    "excellent": "ping_excellent",
    "good": "ping_good",
    "fair": "ping_fair",
    "poor": "ping_poor",
    "critical": "ping_critical",
}


def get_ping_status(ms, theme=None):
    """Return (status_label, color) for a given ping value.

    Pass the active theme dict to get light/dark-safe colors (e.g. a darker
    green on light mode for contrast against white). If no theme is given,
    falls back to the original dark-mode colors — old call sites that don't
    know about themes yet keep working unchanged."""
    if ms is None:
        status = "unknown"
    elif ms < PING_THRESHOLDS["excellent"]:
        status = "excellent"
    elif ms < PING_THRESHOLDS["good"]:
        status = "good"
    elif ms < PING_THRESHOLDS["fair"]:
        status = "fair"
    elif ms < PING_THRESHOLDS["poor"]:
        status = "poor"
    else:
        status = "critical"

    color = theme[_PING_THEME_KEY[status]] if theme else _DEFAULT_PING_COLORS[status]
    return status, color
