# PingGuard — Claude Code Context

Network/ping monitor for gamers. Checks ping before you get stuck in a high-latency match. v3 roadmap: full network diagnostic tool (free, more capable than PingPlotter).

---

## Tooling — Claude Code (Adopted Session 17)

- **Primary hands-on work** happens via Claude Code run directly in the project folder, not by uploading files into chat.
- **This file (`CLAUDE.md`)** is generated from `PingGuard_Context.md` — read automatically at the start of every session. When `PingGuard_Context.md` is updated, ask Claude Code to regenerate this file from the new version.
- **Chat stays the planning and narrative layer** — deciding what to do, reviewing diffs in plain English, dictating via voice-to-text. Claude Code is for file edits, running the app, builds, and git operations.
- **Established working pattern:** for anything with a side effect (editing a file, running a command, deleting/merging data), show the exact diff or exact before/after first; confirm before applying. This pattern is load-bearing, not optional.
- **Hard standing rule:** when a description of file or code content ("the function does X," "added 1 line removed 1 line," "the dict checks for Y") doesn't match — or hasn't yet been checked against — the literal content, ask for the literal content before proceeding. This applies equally to summaries of data, summaries of code, and summaries of tool output. A description of correct-sounding behavior is not the same as correct behavior.

---

## Current State

- **Version:** v2.1.0 shipped. v2.2.0 (per-game region management) in progress — see Roadmap.
- **Platform:** Windows only (macOS/Linux Beta existed in v2.0.4 but pipeline is Windows-only now).
- **Live on:** `jackalnode.itch.io/pingguard` and `github.com/JackalNode/pingguard`
- **CI/CD:** GitHub Actions — tag push → cloud build → installer attached to release automatically.
- **Auto-update:** wired via `updater.py`.
- **Process detection:** confirmed working live (Session 17) — Apex Legends "Running" bar and ping history both updated correctly during a real launch.
- **`trace_connections.py` (Session 17):** standalone script (not part of the shipped app) that uses `psutil` to list a running game's real active network connections. Built to verify Warzone's server address; reusable for auditing any other game, and a proof-of-concept for the psutil-based Server Address auto-fill idea.

---

## Project Paths

- **Project root:** `C:\Users\natha\Desktop\Project\PingGuard v3\PingGuard`
- **All source files** sit flat in the project root — no `core/` or `src/` subfolder.
- **PyInstaller output:** `dist\PingGuard.exe`
- **Inno Setup output:** `installer_output\` (SourcePath-relative in the `.iss` file)
- **User data (`games.json`):** `C:\Users\natha\AppData\Roaming\PingGuard\games.json` — outside the git repo, never tracked.
- **`trace_connections.py`** sits flat in the root alongside everything else but is a standalone research tool — not imported by, or part of, the shipped app.
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

**Tag format:** only clean tags like `v2.1.0` trigger the workflow (`v[0-9]*.[0-9]*.[0-9]*`). Suffixed tags are intentionally ignored.

**Release rhythm:** individual fixes get committed and pushed as done — hygiene only. The version bump → tag → installer → itch.io sequence happens once, batched, when a whole minor version's checklist is complete.

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
- **A game's name is its sole identity everywhere in the data model** — `update_ping()`, `remove_game()`, and `update_game()` all match purely by `game["name"] == name`. This is now actively enforced: `add_game()` refuses to append a game whose name already exists (case-insensitive), returning `False` on duplicate and `True` on success. Any caller must check the return value and surface a clear message on failure.
- `update_ping()` breaks on the first name match. This is only safe because duplicate names are structurally prevented at `add_game()`. If that guard is ever removed or bypassed, the silent data-corruption bug (ping results written to the wrong entry, no error) returns immediately.
- Webhook lives in `constants.py` only — never in settings, never user-configurable.
- Single instance lock port: **47823** (StartGuard uses 47824).
- HTTP calls use `requests` — Discord blocks urllib.
- One authoritative version string: `app.setApplicationVersion()` in `main.py`.
- `.iss` paths always `SourcePath`-relative.

### Regional variants
- Regional game variants are **always standalone, independent entries** — never a blended endpoint list with fallback.
- `tcp_ping()` counts a refused TCP connection as a success — so the first endpoint in a fallback list almost always wins and later ones are dead code. This is why blended endpoints are banned.
- **AWS regional endpoints** are the trusted benchmark for "which region is closest" testing:
  - NA: `ec2.us-east-1.amazonaws.com`
  - EU: `ec2.eu-west-1.amazonaws.com`
  - Asia: `ec2.ap-southeast-1.amazonaws.com`
  - SA: `ec2.sa-east-1.amazonaws.com`
  - OCE: `ec2.ap-southeast-2.amazonaws.com`
  - Africa: `ec2.af-south-1.amazonaws.com`

### Exe / process matching
- `exe`, `exe_mac`, `exe_linux` can be **a single string or a list of accepted aliases**. Use a list when a publisher renames an executable.
- `exe` matching only affects two secondary features: the "▶ Running" badge and check-on-launch. Never the core ping test (purely host/port).
- A future "game stopped showing as running" report: check whether the publisher renamed the exe first, then add the new name to the alias list.

### `migrate_game_endpoints()` — per-game entries
- **Each entry in the `fixes` dict must carry its own `is_stale` lambda and its own `region_note`** — never a shared/broad condition or hardcoded label across multiple games.
- A correct new address for one game can coincidentally collide with another game's old-bad-address prefix check. Proven in Session 17: Warzone's real `185.34.106.103` starts with `185.`, which is the same prefix CS2/Dota2's staleness check matches. A shared check would have re-triggered on Warzone's already-correct entry forever.
- `migrate_game_endpoints()` runs unconditionally on every `GameManager.load()`. Its return value is OR'd with `migrate_game_regions()`'s, and `self.save()` fires once if either returned `True`.

### Call of Duty / Demonware architecture
- **Call of Duty's actual game servers run on Demonware (Activision's own networking subsidiary), confirmed via RIPE WHOIS — not Battle.net.** Battle.net is only the PC login/launcher layer for Activision titles. For genuine Blizzard titles (Overwatch, Diablo, WoW), Battle.net *is* the real backend — this distinction matters when choosing what to ping.
- Demonware does not appear to expose fixed, named regional addresses the way Battle.net does. Matchmaking dynamically assigns datacenters. This is why a full Overwatch-2-style regional split isn't currently available for Warzone.
- The proven method for auditing any game's real server: run `trace_connections.py` during a live session, identify stable non-CDN ESTABLISHED connections, run WHOIS to confirm ownership, then verify via `tcp_ping()` before touching any code. A suspiciously low result (like 7ms from Cape Town to a "distant" server) means CDN/anycast — not a real datacenter.

### Dynamic datacenter assignment (Session 18 — generalizes Warzone finding)
- **Dynamic per-match datacenter assignment is not Call-of-Duty-specific.** Confirmed directly via live in-game evidence on Apex Legends: PingGuard's verified, WHOIS-confirmed AWS endpoint (`us-east-1`) didn't match the in-game datacenter readout (`sa-east-1`) on a later match.
- Any title using cloud-hosted, matchmaking-assigned dedicated servers should be assumed to share this limitation by default during future audits, rather than treated as a special case to check for individually.
- A single hardcoded endpoint is still a strict improvement over CDN-shadowed numbers — it will read correctly when a match lands in the same region. Solving it properly requires real-time per-match server detection (v3 scope).

### Theme system
- `theme.py` is the single source of truth for all colors. Two dicts: `DARK` and `LIGHT`, identical key sets (39 tokens).
- Widgets with direct `settings` access compute their own theme. Nested widgets receive a resolved `theme` dict as a constructor parameter.
- Live re-theming via `MainWindow.apply_theme()` — no restart needed.
- Ping-status colors live in `games.py` (`get_ping_status(ms, theme=None)`), not `theme.py`.
- Token-dictionary pattern is standard for all future JackalNode apps.

---

## Data Integrity — Duplicate Game Names (Discovered & Fixed Session 17)

**The bug:** `GameManager.add_game()` blindly appended without checking for an existing name. With two entries sharing a name, `update_ping()`'s first-match-wins loop wrote all ping results to whichever entry came first — regardless of which was enabled or being monitored. Zero error messages.

**The fix:**
1. `add_game()` checks case-insensitively for an existing name before appending. Returns `False` on duplicate, `True` on success.
2. `_on_add_game()` in `main_window.py` checks the return value and shows `QMessageBox.warning("A game named '...' is already in your list.")` on failure.
3. Verified: exactly one call site for `add_game()` in the whole codebase (`main_window.py`). `setup_wizard.py` does not call it.
4. Verified: no edit-existing-game UI exists — `update_game()` exists in `settings.py` but has no UI caller. Warning message was worded to not reference a feature that doesn't exist.

---

## Call of Duty: Warzone — Endpoint Fix (Session 17)

**What was wrong:** the second endpoint `172.64.155.188:3074` was Cloudflare anycast (falls inside `172.64.0.0/13`, Cloudflare's documented public egress range) — the same class of false positive as the Battle.net CDN issue that broke the first setup-wizard attempt in Session 15.

**How the replacement was found:** built `trace_connections.py` to list a running game's real connections via `psutil`. Ran it during a live Warzone match. `185.34.106.103:3074` appeared in every run with status `ESTABLISHED`. WHOIS confirmed `185.34.106.0/24` is registered to Demonware Limited. Verified via `tcp_ping()`: 248ms from Cape Town — a high, physically plausible number for a genuinely distant datacenter.

**What was fixed:** `172.64.155.188:3074` → `185.34.106.103:3074` in `games.py`. `migrate_game_endpoints()` updated so existing installs get corrected too. `eu.battle.net:443` left untouched.

**What this is not:** a regional split. Demonware doesn't expose fixed regional addresses, so there's no second confirmed address to split into. This is a verified endpoint correction only.

**Open questions remaining:** whether `eu.battle.net` itself is measuring the right thing (it's Blizzard's login layer, not Demonware's game backend); the GCP address on port 1119 (`35.204.122.188`) seen during the trace (same port as WoW's real game-data endpoint in `games.py`) — not investigated further.

---

## Apex Legends — Endpoint Fix (Session 18)

**What was wrong:** the entry blended `eaassets-a.akamaihd.net:443` (Akamai CDN) with `159.153.64.1:37015`. Because `ping_game()` is first-success-wins and TCP refusals count as success, the CDN endpoint was shadowing every ping — Apex's displayed latency was measuring Akamai, not the game server.

**How the replacement was found:** `trace_connections.py` run 5 times during a live match. `100.50.20.250:9000` was the only non-443 connection, present and `ESTABLISHED` in every run. WHOIS: AWS `AMAZON-IAD` (Amazon Data Services Northern Virginia). Verified via `tcp_ping()`: 209ms from Cape Town — sane for Virginia.

**What was fixed:** `games.py` endpoints replaced entirely with `{"host": "100.50.20.250", "port": 9000}`. `region_note` corrected from `"EU servers"` to `"EA servers (US-East, AWS)"`. `migrate_game_endpoints()` in `settings.py` updated with a new `'Apex Legends'` entry (own `is_stale`, own `region_note`) — collision-checked against all existing entries before applying.

**Known accepted limitation:** live verification confirmed Apex's matchmaking dynamically assigns datacenters per match — PingGuard showed `us-east-1` (208ms) while the in-game readout showed `sa-east-1` (172ms). The fixed endpoint is correct when a match lands in `us-east-1`; it can't follow a player to a different datacenter. Same shape as Warzone's dynamic-assignment problem. Real fix is v3 real-time detection.

**`159.153.64.1` status:** genuine EA-owned IP (ARIN direct allocation), not a CDN — but never appeared in 5 live traces and timed out on `tcp_ping()`. Left as an open question: port 37015 suggests UDP-only game data, which wouldn't show in a TCP trace regardless of whether the server is retired.

---

## File Inventory

| File | Notes |
|------|-------|
| `main.py` | Version string `2.1.0`. AppUserModelID set before QApplication. |
| `app.py` | Never reads `game["exe"]` directly — only consumes `ping_worker.get_running_games()`. |
| `main_window.py` | `_on_add_game()` checks `add_game()` return value; shows warning on duplicate. Never reads `game["exe"]` directly. |
| `settings.py` | `GameManager`. `add_game()` enforces unique names (case-insensitive), returns True/False. `migrate_game_endpoints()` restructured: each entry in `fixes` carries its own `is_stale` lambda and `region_note` — CS2, Dota 2, Call of Duty: Warzone, and Apex Legends all present. `migrate_game_regions()` unchanged. `update_game()` exists but has no UI caller. |
| `games.py` | `DEFAULT_GAMES`. Apex exe is `["r5apex.exe", "r5apex_dx12.exe"]`. Apex endpoint is `100.50.20.250:9000` (WHOIS-confirmed AWS/EA, region_note "EA servers (US-East, AWS)"). OW2 split into (EU)/(NA). Warzone second endpoint is `185.34.106.103:3074` (confirmed Demonware). |
| `ping_engine.py` | `get_process_names_for_game()` + `_as_list()` helper. `check_running_games()` matches alias-set overlap. `tcp_ping()` reused directly to verify both Warzone and Apex endpoints. `ping_game()` is first-success-wins — walks endpoints in order, returns on first success. |
| `game_detector.py` | Scans Steam/Epic/Riot/Battle.net for installed games. All detectors independently try/except. |
| `add_game_dialog.py` | Detected-games dropdown, Browse button, game-request report hook. Dialog height 420×555. Server Address field has label, tooltip, and hint. All confirmed working via live testing. |
| `reporter.py` | `send_report()` + `send_game_request()`. Webhook from `constants.py`. |
| `setup_wizard.py` | First-run wizard. Region step before games step. AWS endpoints for latency probing. Does not call `add_game()`. |
| `theme.py` | Dark/light token dicts. Stable since Session 14. |
| `logger.py` | CSV session logging, 30-day auto-cleanup. Discovered Session 15, not modified. |
| `trace_connections.py` | Standalone diagnostic script — not part of the shipped app. Uses `psutil` to list a named running process's active connections. Built for Warzone endpoint verification; reusable for any game audit going forward. |
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
- Browse button opens to the detected game's install folder — deliberately not auto-filling the exe field.
- **Known limitation:** no way to auto-fill Server Address for a game not in `games.py`. `trace_connections.py` proves the psutil live-connection approach is viable in principle, but real connection lists are noisy (up to 9 simultaneous connections observed in one Warzone session across CDN/cloud/game traffic) — would need real filtering logic before going anywhere near the UI. Still future work.

---

## v2.2.0 Remaining Work

- `🔲` Audit remaining ~15 `DEFAULT_GAMES` entries for blended-region-fallback issue — `trace_connections.py` + WHOIS is now the proven method. Path of Exile and World of Warcraft are next.
- `🔲` Audit remaining default games for exe staleness
- `🔲` Real per-game region management UI
- `🔲` Per-game ping thresholds
- `🔲` Real "edit existing game" UI — `update_game()` exists in `settings.py` but has no caller anywhere
- `🔲` Investigate psutil-based Server Address auto-fill in the actual Add Game dialog (filtering logic needed before it's UI-ready)
- `🔲` Confirm `remove_game()` has a visible button wired to it end to end

---

## Roadmap

| Version | Status | Description |
|---|---|---|
| v2.0.5 / v2.0.6 | ✅ Shipped | Bug fixes, infrastructure parity |
| v2.1.0 | ✅ Shipped | Icon, light/dark theme, Settings cleanup |
| v2.2.0 | 🟡 In progress | Per-game region management (see checklist above) |
| v2.3.0 | Tentative | Game search / server auto-fill — psutil approach is the leading candidate; only proceeds if a workable implementation is confirmed |
| v3.0.0 | Future | Network diagnostics: traceroute, hop latency, ISP ID, packet loss. Real-time per-match server detection is a confirmed motivation (dynamic datacenter assignment observed on both Warzone and Apex). Elevation approach (scapy vs. raw sockets) not yet decided. |

---

## Open Questions

- **Whether `eu.battle.net` is measuring the right thing for Warzone** — it's the Blizzard login layer, not Demonware's game backend. May only reflect login-service latency, not real match-server latency.
- **GCP address on port 1119** (`35.204.122.188`) seen during Warzone trace — same port as WoW's real game-data endpoint in `games.py`. Not investigated.
- **Real-time per-match server detection** — confirmed on both Warzone (Demonware) and Apex (AWS multi-region) that a single hardcoded endpoint can't represent "the server you'd actually play in" for titles with dynamic datacenter assignment. `trace_connections.py` proves the psutil approach works; turning it into a live in-app feature is the real fix. v3 scope.
- **Path of Exile (`45.33.26.109:20481`) and World of Warcraft (`eu.actual.battle.net:1119`)** — next in the audit queue using the proven `trace_connections.py` + WHOIS method.
- **Edit/remove game UI:** `update_game()` has no caller. Confirm `remove_game()` has a visible button wired to it before assuming removal works end to end.
- **psutil live-connection detection:** viable in principle (proven by `trace_connections.py`), but needs filtering logic before it can be a UI feature.
- **macOS / Linux:** pipeline is Windows-only; needs dedicated session when ready.
- **v2.3.0 data source:** psutil approach is the candidate to investigate first.
- **v3.0.0 elevation:** scapy vs. manual raw sockets — not decided.
- **Tray icon:** still shows generic blue circle instead of shield art. Dev's call to leave as low priority.
