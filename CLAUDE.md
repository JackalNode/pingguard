# PingGuard — Claude Code Context

Network/ping monitor for gamers. Checks ping before you get stuck in a high-latency match. v3 roadmap: full network diagnostic tool (free, more capable than PingPlotter).

---

## Tooling — Claude Code (Adopted Session 17)

- **Primary hands-on work** happens via Claude Code run directly in the project folder, not by uploading files into chat.
- **This file (`CLAUDE.md`)** is generated from `PingGuard_Context.md` — read automatically at the start of every session. When `PingGuard_Context.md` is updated, ask Claude Code to regenerate this file from the new version.
- **Chat stays the planning and narrative layer** — deciding what to do, reviewing diffs in plain English, dictating via voice-to-text. Claude Code is for file edits, running the app, builds, and git operations.
- **Established working pattern:** for anything with a side effect (editing a file, running a command, deleting/merging data), Claude Code shows the exact diff or exact before/after first; confirm before it's applied.
- **Process lesson (Session 17):** when Claude Code's summary of file content contradicts something directly observed on screen, ask for the literal raw data, not a re-summarized table. This caught a backwards conclusion before any data was touched.

---

## Current State

- **Version:** v2.1.0 shipped. v2.2.0 (per-game region management) in progress — see Roadmap.
- **Platform:** Windows only (macOS/Linux Beta existed in v2.0.4 but pipeline is Windows-only now).
- **Live on:** `jackalnode.itch.io/pingguard` and `github.com/JackalNode/pingguard`
- **CI/CD:** GitHub Actions — tag push → cloud build → installer attached to release automatically.
- **Auto-update:** wired via `updater.py`.
- **Process detection:** confirmed working live (Session 17) — Apex Legends "Running" bar and ping history both updated correctly during a real launch.

---

## Project Paths

- **Project root:** `C:\Users\natha\Desktop\Project\PingGuard v3\PingGuard`
- **All source files** sit flat in the project root — no `core/` or `src/` subfolder.
- **PyInstaller output:** `dist\PingGuard.exe`
- **Inno Setup output:** `installer_output\` (SourcePath-relative in the `.iss` file)
- **User data (`games.json`):** `C:\Users\natha\AppData\Roaming\PingGuard\games.json` — lives outside the git repo, never tracked, no `.gitignore` concern.
- **Old folder** (`PingGuard v2\pingguard`) is retired — ignore it.

---

## How to Ship a New Version

1. Bump version in **two places only:**
   - `app.setApplicationVersion("x.x.x")` in `main.py`
   - `#define MyAppVersion "x.x.x"` in `PingGuard.iss`
2. Commit, push, tag:
   ```
   git add .
   git commit -m "vX.X.X"
   git push
   git tag vX.X.X
   git push origin vX.X.X
   ```
3. GitHub Actions builds automatically; green check = Release with installer attached.
4. Upload installer to itch.io.

**Tag format:** only clean tags like `v2.1.0` trigger the workflow (`v[0-9]*.[0-9]*.[0-9]*`). Suffixed tags (e.g. `v2.1.0-debug`) are intentionally ignored.

**Release rhythm:** individual fixes get committed and pushed as they're done — that's just hygiene. The version bump → tag → installer → itch.io sequence happens once, batched, when a whole minor version's checklist is complete — not after every single fix.

---

## GitHub Actions Pipeline

- **File:** `.github/workflows/build.yml`
- **Secret required:** `DISCORD_REPORT_WEBHOOK` in repo Settings → Secrets
- **Workflow permissions:** "Read and write" in repo Settings → Actions → General
- **Version injection:** passed from git tag into Inno Setup via `/DMyAppVersion=` flag

### Known pipeline pitfalls (don't repeat):
- `OutputDir` in `.iss` must be `{#SourcePath}installer_output` — bare folder name breaks on cloud runner
- Version must come from the tag, not hardcoded — hardcoding causes filename mismatches
- `requirements.txt` must stay in sync with imports — `requests` and `packaging` were missing and caused launch crashes

---

## Architecture Decisions (Standing Rules)

### Data model and identity
- `DEFAULT_GAMES` in `games.py` **only runs once** — the very first launch. After that, `games.json` on disk is the real source of truth. Any structural change to `DEFAULT_GAMES` **must** be paired with a migration in `settings.py`'s `GameManager.load()`.
- **A game's name is its sole identity everywhere in the data model** — `update_ping()`, `remove_game()`, and `update_game()` all match purely by `game["name"] == name`. This is now actively enforced: `add_game()` refuses to append a game whose name already exists (case-insensitive). If that guard is ever removed or bypassed, `update_ping()`'s first-match-wins behavior silently writes ping results to the wrong entry with no error.
- `add_game()` returns `True` on success, `False` on a duplicate name. Any caller must check the return value and surface a clear message on failure — never assume success.
- Webhook lives in `constants.py` only — never in settings, never user-configurable.
- Single instance lock port: **47823** (StartGuard uses 47824).
- HTTP calls use `requests` — Discord blocks urllib.
- One authoritative version string: `app.setApplicationVersion()` in `main.py`.
- `.iss` paths always `SourcePath`-relative.

### Regional variants
- Regional game variants are **always standalone, independent entries** — never a blended endpoint list with fallback. "Overwatch 2 (EU)" and "Overwatch 2 (NA)" are the worked example.
- `tcp_ping()` counts a refused TCP connection as a success ("server reachable, just said no") — so the first endpoint in a fallback list almost always wins and later ones are dead code. This is why blended endpoints are banned.
- **AWS regional endpoints** are the trusted benchmark for "which region is closest" testing:
  - NA: `ec2.us-east-1.amazonaws.com`
  - EU: `ec2.eu-west-1.amazonaws.com`
  - Asia: `ec2.ap-southeast-1.amazonaws.com`
  - SA: `ec2.sa-east-1.amazonaws.com`
  - OCE: `ec2.ap-southeast-2.amazonaws.com`
  - Africa: `ec2.af-south-1.amazonaws.com`

### Exe / process matching
- `exe`, `exe_mac`, `exe_linux` can be **a single string or a list of accepted aliases**. Use a list when a publisher renames an executable so old and new installs both match.
- `exe` matching **only ever affects two secondary features**: the "▶ Running" badge and check-on-launch. It has no path to the core ping test (purely host/port). A stale `exe` degrades those features gracefully — it cannot break ping accuracy.
- A future "game stopped showing as running" report: check whether the publisher renamed the exe first, then add the new name to the alias list.
- Custom games added via Add Game store a plain string for `exe` — `_as_list()` in `ping_engine.py` normalizes it transparently.

### Theme system
- `theme.py` is the single source of truth for all colors. Two dicts: `DARK` and `LIGHT`, identical key sets enforced by design (39 tokens).
- Widgets with direct `settings` access compute their own theme. Nested widgets receive a resolved `theme` dict as a constructor parameter.
- Live re-theming via `MainWindow.apply_theme()` — no restart needed.
- Ping-status colors live in `games.py` (`get_ping_status(ms, theme=None)`), not in `theme.py`.
- This token-dictionary pattern is standard for all future JackalNode apps.

---

## Data Integrity — Duplicate Game Names (Discovered & Fixed Session 17)

**The bug:** `GameManager.add_game()` blindly appended without checking for an existing name. With two entries sharing a name, `update_ping()`'s first-match-wins loop wrote all ping results to whichever entry came first in the list — regardless of which one was enabled or being actively monitored. Zero error messages, zero visible signs.

**The fix:**
1. `add_game()` now checks case-insensitively for an existing name before appending. Returns `False` on duplicate, `True` on success.
2. `_on_add_game()` in `main_window.py` checks the return value and shows `QMessageBox.warning("A game named '...' is already in your list.")` on failure.
3. Verified: exactly one call site for `add_game()` in the whole codebase (`main_window.py`). `setup_wizard.py` does not call it.
4. Verified: no edit-existing-game UI exists anywhere — `update_game()` exists in `settings.py` but has no UI caller. Warning message was worded to not reference a feature that doesn't exist.

**Why this matters beyond the one case that surfaced it:** any game name, default or custom, could hit this failure mode. The fix protects every game going forward.

---

## File Inventory

| File | Notes |
|------|-------|
| `main.py` | Version string `2.1.0`. AppUserModelID set before QApplication. |
| `app.py` | Never reads `game["exe"]` directly — only consumes `ping_worker.get_running_games()`. |
| `main_window.py` | `_on_add_game()` checks `add_game()` return value; shows warning on duplicate. Never reads `game["exe"]` directly. |
| `settings.py` | `GameManager`. `add_game()` now enforces unique names (case-insensitive), returns True/False. `migrate_game_regions()` + `migrate_game_endpoints()` run on every load. `update_game()` exists but has no UI caller. |
| `games.py` | `DEFAULT_GAMES`. Apex exe is `["r5apex.exe", "r5apex_dx12.exe"]`. OW2 split into (EU)/(NA). Module docstring explains string-or-list convention. |
| `ping_engine.py` | `get_process_names_for_game()` (returns list) + `_as_list()` helper. `check_running_games()` matches alias-set overlap. Minecraft special-case untouched. Confirmed working live with real Apex launch (Session 17). |
| `game_detector.py` | Scans Steam/Epic/Riot/Battle.net for installed games. All detectors independently try/except. |
| `add_game_dialog.py` | Detected-games dropdown, Browse button, game-request report hook. Dialog height 420×555. Server Address field has label, tooltip, and hint. All confirmed working via live testing (Session 17). |
| `reporter.py` | `send_report()` + `send_game_request()`. Webhook from `constants.py`. |
| `setup_wizard.py` | First-run wizard. Region step before games step. AWS endpoints for latency probing. Does not call `add_game()`. |
| `theme.py` | Dark/light token dicts. Stable since Session 14. |
| `logger.py` | CSV session logging, 30-day auto-cleanup. Discovered Session 15, not modified. |
| `constants.py` | Discord webhook (gitignored). |
| `updater.py` | Auto-update shared logic. |

---

## Add Game — Auto-Detection

`game_detector.py` scans four launchers:

| Launcher | Source | Notes |
|---|---|---|
| Steam | `steamapps/libraryfolders.vdf` + `appmanifest_*.acf` | Regex-parsed, no new deps |
| Epic | `C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests\*.item` | JSON |
| Riot | `C:\ProgramData\Riot Games\RiotClientInstalls.json` | JSON |
| Battle.net | Windows registry uninstall keys (filtered by publisher) | Avoids binary `product.db`. Games "ready to install" but not installed may be absent — acceptable. |

- Zero new dependencies (all stdlib: `winreg`, `json`, `os`, `re`).
- `detect_all_games()` merges, de-dupes by name (case-insensitive), sorts alphabetically.
- Runs on `GameDetectionWorker` (QThread) so the dialog never freezes.
- Browse button opens to the detected game's install folder — deliberately not auto-filling the exe field (no launcher reliably exposes the exact executable with confidence).
- **Known remaining limitation:** no way to auto-fill Server Address for a game not already in `games.py` — the four launchers only know what's installed, not what server it connects to. Idea flagged for investigation: use `psutil` (already in the project for running-game detection) to list a running game's active remote connections as a "pick from what it's actually talking to" alternative. Not yet investigated — needs the same verify-before-building discipline used for the AWS-endpoint wizard.

---

## v2.2.0 Remaining Work

- `🔲` Call of Duty: Warzone region split — second endpoint (`172.64.155.188`) may be Cloudflare anycast; needs verification before splitting
- `🔲` Audit remaining ~16 `DEFAULT_GAMES` entries for blended-region-fallback issue
- `🔲` Audit remaining default games for exe staleness (lower priority — only surfaces when a publisher renames something)
- `🔲` Real per-game region management UI (enable/disable regional variants post-setup)
- `🔲` Per-game ping thresholds
- `🔲` Real "edit existing game" UI — `update_game()` exists in `settings.py` but has no UI caller anywhere; also worth confirming `remove_game()` has a visible button wired to it before assuming removal is solved
- `🔲` Investigate psutil-based live-connection detection for Server Address auto-suggest

---

## Roadmap

| Version | Status | Description |
|---|---|---|
| v2.0.5 / v2.0.6 | ✅ Shipped | Bug fixes, infrastructure parity |
| v2.1.0 | ✅ Shipped | Icon, light/dark theme, Settings cleanup |
| v2.2.0 | 🟡 In progress | Per-game region management (see checklist above) |
| v2.3.0 | Tentative | Game search with auto-populated server info — psutil live-connection idea is the leading candidate direction; only proceeds if investigation confirms it works |
| v3.0.0 | Future | Network diagnostics: traceroute, hop latency, ISP ID, packet loss. Raw sockets need elevation — scapy vs. manual raw sockets not yet decided. |

---

## Open Questions

- **CoD Warzone endpoint:** `172.64.155.188` — genuine NA infrastructure or Cloudflare anycast? Verify before splitting.
- **Edit/remove game UI:** `update_game()` exists but has no caller. `remove_game()` exists — confirm there's a visible button wired to it before assuming removal works end to end.
- **psutil live-connection detection:** investigate whether listing a running game's active remote connections is a viable Server Address auto-suggest. Verify it actually works before building UI around it.
- **macOS / Linux:** pipeline is Windows-only; needs dedicated session when ready.
- **v2.3.0 data source:** no confirmed workable source for game server info yet — psutil idea is the candidate to investigate first.
- **v3.0.0 elevation:** scapy vs. manual raw sockets — not decided.
- **Tray icon:** still shows generic blue circle instead of shield art. Dev's call to leave as low priority.
