# PingGuard — Context Document
> Paste alongside JackalNode_Context.md at the start of any PingGuard session — though as of Session 17, the primary working method has shifted (see Tooling section below).
> Built fresh in Session 12, modeled on StartGuard_Context.md's structure (StartGuard is the blueprint — see master doc Standing Rule #8).
> Last updated: Session 17 — Claude Code adopted as the primary hands-on tool for PingGuard, with a `CLAUDE.md` (generated from this doc) providing persistent project context. Apex Legends running-badge fix confirmed via a real live launch. That same test surfaced a separate, more serious bug: duplicate game names silently corrupt ping data, with no warning to the user. Found, root-caused, and fixed end to end. New idea flagged for a future session: psutil-based live-connection detection to help with the Server Address field for unlisted games.

---

## What It Is
Network/ping monitor for gamers — checks your gaming ping before you get stuck in a high-ping match. Currently a ping monitor; the v3 roadmap evolves it into a full network diagnostic tool, free and more capable than PingPlotter.

---

## Confirmed Live URLs (verified directly, Session 12)
- **GitHub repo:** `github.com/JackalNode/pingguard` (lowercase — cosmetic only, but use verbatim in build files)
- **itch.io:** `jackalnode.itch.io/pingguard`

---

## Tooling — Claude Code (Adopted Session 17)
- **Primary hands-on work now happens via Claude Code**, run directly in the project folder (`cd` into the project, then `claude`), rather than uploading individual files into chat each session.
- **`CLAUDE.md`** lives in the project root and is generated from this context doc — Claude Code reads it automatically at the start of every session in that folder, so the project history doesn't need to be re-pasted.
- **When this doc is updated** (end of every session, same as always), the dev should re-generate `CLAUDE.md` by dropping the updated doc into the project folder and asking Claude Code to refresh it from the new version.
- **Chat (this doc, this conversation) stays the planning and narrative layer** — deciding what to do, reviewing diffs in plain English, working through "why," dictating longer thoughts via voice-to-text. Claude Code is for the hands-on file edits, running the app, running builds, and git operations against the real project.
- **Established working pattern:** for anything with a side effect — editing a file, running a command that changes state, deleting/merging data — Claude Code shows the exact diff or exact before/after first; the dev (often relaying through this chat) confirms before it's applied. This matched how the Session 17 data bug below was handled, including catching a wrong conclusion in Claude Code's own first read of the situation before any data was touched.
- **Login is account-wide** — once logged in for PingGuard, no second login needed to use Claude Code in the StartGuard folder later.
- Same Pro plan, same usage pool as chat — heavy Claude Code sessions and heavy chat sessions on the same day can compound toward the same limit.

---

## Current State
- **Version:** v2.1.0 shipped and live. v2.2.0 (per-game region management) is **in progress, not yet shipped** — see Session 15/16/17 below for what's done vs. still open.
- **Platforms:** Windows (live). macOS / Linux — Beta builds existed in v2.0.4 but not yet rebuilt. See Open Questions.
- **Live on itch.io** under the JackalNode account, same pricing model as StartGuard ($0 or donate)
- **GitHub Actions pipeline:** ✅ Live and working — tag push → cloud build → installer attached to release automatically
- **Auto-update:** ✅ Wired in via shared `updater.py`
- **Report button:** ✅ Fixed — webhook in `constants.py`, gitignored. Sibling "couldn't find this game" report path also live (see Session 15).
- **Icon:** ✅ Real PingGuard-specific art, confirmed across title bar, taskbar, tray, and Windows notifications.
- **Light/Dark theme:** ✅ Built and shipped — full token-based system, toggle lives in Settings → Appearance, applies live with no restart required.
- **Settings dialog:** dead "Reporting" tab removed entirely — single flat layout now, no tabs.
- **Add Game:** ✅ Auto-detects installed games from Steam, Epic, Riot, and Battle.net (Session 15). ✅ Server Address field clarity fixed (Session 16). ✅ Now refuses duplicate game names with a clear warning instead of silently corrupting data (Session 17 — see Data Integrity section below).
- **Region separation:** 🟡 Architecture and migration built and validated (Overwatch 2 only, as the worked example). Not yet rolled out to other affected games. See Session 15.
- **Process detection (running-game matching):** ✅ Hardened (Session 16), ✅ **confirmed working via a real live Apex Legends launch (Session 17)** — the "▶ Running" bar and ping history both updated correctly in real time.

---

## Project & Build Paths
- **Project path:** `C:\Users\natha\Desktop\Project\PingGuard v3\PingGuard`
- **PyInstaller output:** `dist\PingGuard.exe` inside project root
- **Inno Setup OutputDir:** `installer_output\` (SourcePath-relative)
- **GitHub repo:** `github.com/JackalNode/pingguard`
- **itch.io:** `jackalnode.itch.io/pingguard`
- **Folder structure confirmed (Session 15, via screenshot):** everything sits flat in the project root — no `core/` subfolder. `game_detector.py` lives here too, alongside `games.py`, `reporter.py`, etc.
- **User data location:** `games.json` lives under the dev's AppData folder (confirmed Session 17 — separate from the git repo entirely, never tracked, no `.gitignore` concern).

> Note: `PingGuard v2\pingguard` on Desktop is the old manual-build folder — retired. `PingGuard v3\PingGuard` is the live git repo going forward.

---

## How To Ship a New Version
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
3. Watch Actions tab — green check = Release published with installer attached automatically.
4. Upload new installer to itch.io.

**Tag format matters:** only clean tags like `v2.1.0` trigger the workflow. Tags with suffixes (e.g. `v2.1.0-debug`) are intentionally ignored by the trigger pattern `v[0-9]*.[0-9]*.[0-9]*`.

**Established release rhythm (reconfirmed Session 17):** individual fixes get committed and pushed to GitHub as they're done — that's just hygiene. The version bump → tag → installer → itch.io sequence happens once, batched, when a whole minor version's checklist (e.g. all of v2.2.0) is actually complete — not after every single fix.

---

## GitHub Actions Pipeline
- **File:** `.github\workflows\build.yml`
- **Trigger:** push of a tag matching `v[0-9]*.[0-9]*.[0-9]*`
- **Secret required:** `DISCORD_REPORT_WEBHOOK` — set in repo Settings → Secrets and variables → Actions
- **Workflow permissions:** "Read and write" — set in repo Settings → Actions → General
- **Version passing:** workflow passes version from git tag into Inno Setup via `/DMyAppVersion=` flag
- **Output:** `installer_output/PingGuard_Setup_vX.X.X.exe` attached to GitHub Release

### Bugs hit and fixed during pipeline setup (Session 13 — don't repeat):
1. `OutputDir` in `.iss` needs `{#SourcePath}installer_output` — plain folder name breaks on cloud machine
2. Inno Setup version must be passed from git tag via `/DMyAppVersion=` — hardcoding causes filename mismatch
3. Tag trigger pattern `v*` matches debug tags — use `v[0-9]*.[0-9]*.[0-9]*` to exclude them
4. `requests` and `packaging` missing from `requirements.txt` — caused `No module named 'requests'` crash on launch. Always keep requirements.txt in sync when adding new dependencies.

---

## Theme System — Architecture (Built Session 14)
- **`theme.py`** — single source of truth for every color in the app. Two dicts, `DARK` and `LIGHT`, with identical key sets enforced by design (39 tokens). `get_theme(name)` returns the right dict, falling back to dark on any invalid/missing name.
- **Usage pattern:** widgets with direct `settings` access compute their own theme (`get_theme(settings.get("theme", "dark"))`). Nested widgets without `settings` directly receive the resolved `theme` dict as a constructor parameter.
- **Live re-theming, no restart:** `MainWindow.apply_theme()` re-reads the theme, re-applies the stylesheet, then rebuilds the central widget via `_build_ui()`. Wired to fire automatically whenever Settings is saved.
- **Ping-status colors** live in `games.py`, not `theme.py` — `get_ping_status(ms, theme=None)` takes an optional theme parameter, backward-compatible with old call sites.
- Full bug list and file-by-file detail preserved from Session 14 — see prior version of this doc if needed; trimmed here to keep this doc focused on current/active work.

---

## Add Game — Auto-Detection System (Built Session 15, Refined Session 16 & 17)

**The problem this solves:** Add Game previously required users to manually type the game name, process `.exe`, and server host/port — far too technical for PingGuard's actual (non-technical, gamer) audience.

**`game_detector.py`** — sits in the project root alongside `games.py`/`reporter.py`. Scans four launchers for installed games:

| Launcher | Data source | Format | Confidence |
|---|---|---|---|
| Steam | `steamapps/libraryfolders.vdf` + `appmanifest_*.acf` | Valve's text format, hand-parsed via regex (no new dependency) | High — stable, well-documented |
| Epic Games | `C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests\*.item` | Plain JSON | High |
| Riot Games | `C:\ProgramData\Riot Games\RiotClientInstalls.json` | Plain JSON (verified directly — not the messier per-product YAML files some guides reference) | High |
| Battle.net | Windows registry uninstall keys, filtered by publisher (`Blizzard Entertainment`, `Activision`, `Activision Blizzard`) | Standard registry | Medium — deliberately avoids parsing Battle.net's binary `product.db`; known gap is a game shown as "ready to install" but never fully installed won't have a registry entry yet. Acceptable for v1. |

- Zero new dependencies — `winreg`, `json`, `os`, `re`, all stdlib.
- Every detector is independently wrapped in try/except — one broken/missing launcher returns an empty list, never crashes the others or the dialog.
- Every detected game gets a final check that its install folder still exists on disk, to filter out stale/leftover manifests.
- `detect_all_games()` is the single combined entry point: merges all four, de-dupes by name (case-insensitive), sorts alphabetically.
- Runs on a background `QThread` (`GameDetectionWorker` in `add_game_dialog.py`) so opening Add Game never freezes the UI while it scans disk/registry.

**`add_game_dialog.py` — current state:**
- "Installed Games" dropdown above the manual-entry form, populated by `detect_all_games()`. Selecting an entry fills in the Game Name field. **Confirmed working correctly Session 17** via real testing — autofill of the name field was initially suspected as broken but turned out to be working exactly as designed.
- The manual `name_input` field doubles as the "can't find it" fallback — no separate UI mode needed, just a hint label pointing at it.
- **Browse... button** next to Process (.exe) — opens directly to the detected game's install folder so the user picks the real exe instead of typing it. Deliberately *not* auto-filled from detection, since none of the four launchers reliably exposes the exact executable name with full confidence. **Confirmed working correctly Session 17.**
- **Report hook:** "🎮 Tell the dev I couldn't find this game" sends the typed name to Discord via `send_game_request()` in `reporter.py` — separate from `send_report()`.
- **Server Address field — fixed Session 16, confirmed working as intended Session 17:** label "Server Address", tooltip, and hint line pointing to the report fallback. **Known remaining limitation, flagged Session 17 (see Open Questions): there is no way to auto-fill this for a game that isn't already in `games.py`** — the four launcher detectors only know what's installed, not what server a game talks to. Idea proposed for investigation: PingGuard already uses `psutil` for running-game detection; the same library can list a running process's active remote connections, which could turn "type the address from nothing" into "pick from a short list of what this game is actually connecting to right now." Not yet investigated or built — flagged as a future session's design work, not a quick fix, since it needs the same "verify it actually works before building UI around it" discipline used for the AWS-endpoint wizard rebuild.
- **Dialog `setFixedSize`:** 420×555 (bumped from 520 in Session 16 to fit the Server Address hint text).

**Confirmed bug, fixed Session 16, confirmed live Session 17:** Apex Legends' hardcoded `exe` in `DEFAULT_GAMES` was `r5apex.exe`; Browse-detection on the dev's real install found the actual running executable is `r5apex_dx12.exe`. Fixed and generalized into the exe-alias architecture (see Process Detection section). **Session 17: tested with a real live Apex launch — the "▶ Running" bar and ping history chart both updated correctly.**

---

## Data Integrity — Duplicate Game Names Silently Corrupt Ping Data (Discovered & Fixed Session 17)

**How this surfaced:** while live-testing the Apex Legends exe fix, the dev added "Apex Legends" via Add Game to get a fresh entry to test against. This created a **second** "Apex Legends" entry alongside an old, disabled one already sitting in `games.json` from before the Session 16 fix shipped. Nothing in the app warned that the name already existed.

**The actual bug, root-caused via direct file and code inspection (not assumption):**
- `GameManager.add_game()` in `settings.py` blindly appended the new game dict to `self._games` with **no check for an existing name** — `self._games.append(game_dict)`, full stop.
- `GameManager.update_ping()` matches games by `game["name"] == game_name`, walking the list and **breaking on the first match**. With the old disabled entry sitting earlier in the file than the new enabled one, every real ping result for "Apex Legends" was being written into the **old, disabled entry** — not the new, enabled one actually being pinged.
- Net effect: the disabled entry silently accumulated 60 real ping samples over the test session, while the enabled entry — the one actually shown as "running" and actively pinged — stayed permanently empty. This had zero error messages or visible signs; it only surfaced because the dev cross-checked Claude Code's file-read summary against what was actually visible on screen and caught a contradiction.
- **Important process note:** Claude Code's first read of the situation got the two entries backwards (said the disabled one was empty and the enabled one had history) — caught only because the dev compared it against the literal screenshot rather than accepting the summary, and asked for raw file content instead of a re-summarized table. Worth remembering as a general lesson: when an agent's summary of file content contradicts something directly observed, ask for the literal raw data, not a second summary.
- **Bonus finding, no longer reachable but worth remembering:** `remove_game()` uses a list filter (`[g for g in self._games if g["name"] != game_name]`), which would have removed *every* entry sharing that name, including the one with real history — the opposite failure mode from `update_ping()`'s first-match-wins. Not an active bug now that duplicates are blocked at the source, but the underlying assumption — **names are the sole identity of a game in this entire data model** — was already documented as a critical architecture fact back in the Session 15 region-separation work. This is a second, independent confirmation of why that assumption needs enforcing, not just remembering.

**The fix, applied Session 17:**
1. `GameManager.add_game()` now checks case-insensitively whether a game with that exact name already exists in `self._games` before adding. If it does, it returns `False` and adds nothing, instead of silently appending. Returns `True` on a successful add.
2. `main_window.py`'s `_on_add_game()` now checks that return value — on `False`, shows a clear `QMessageBox.warning` ("A game named '...' is already in your list.") instead of silently doing nothing, which was the original, separate UX bug that made this whole problem invisible in the first place.
3. **Confirmed safe before applying:** verified `add_game()` has exactly one call site in the whole codebase (`main_window.py`), so the new return-value contract doesn't silently break anything elsewhere. Verified there is no edit-existing-game UI anywhere in the app — `update_game()` exists in `settings.py` but nothing calls it — so the warning message was worded to not reference a feature that doesn't exist.
4. **One-time manual cleanup of the dev's own `games.json`** (not a permanent migration, since this was caused by the now-fixed `add_game()` bug, not by a `games.py` data change): the two Apex Legends entries were merged into one — kept the original entry's icon (🦅), category, region_note, both endpoints, and its real 60-sample `ping_history`; updated its `exe` field to the alias list `["r5apex.exe", "r5apex_dx12.exe"]`; set `enabled: true`; deleted the second, empty entry. A `games.json.backup` was made before any edit, and the edit was confirmed applied only after verifying the PingGuard process had fully exited (not just the window closed — the system tray icon and background process needed to be gone too, since the app could otherwise overwrite the fix on its next periodic save).
5. **Confirmed working end to end, live:** re-launched the app, Apex showed enabled with its history chart intact (not reset to zero). Deliberately tried to add "Apex Legends" again through Add Game — got the new "already in your list" warning instead of a silent no-op.

**Why this matters beyond Apex:** this wasn't an Apex-specific bug — any game name, default or custom, could have hit this exact failure mode. The fix protects every game going forward, not just the one that happened to surface it.

---

## Process Detection — Architecture (Hardened Session 16, Confirmed Live Session 17)

**Confirmed via direct review of `app.py`, `main_window.py`, and `ping_engine.py`:** the `exe` field is used *only* for "is this game currently running" detection inside `PingWorker.check_running_games()` in `ping_engine.py`. It has zero connection to the actual ping test (`ping_game()` / `tcp_ping()`), which runs purely off `host`/`port`. Neither `app.py` nor `main_window.py` reads `exe` directly — they only consume the already-resolved running-game names that `ping_engine.py` hands back.

**Practical consequence:** a stale/wrong `exe` value can never break ping accuracy for a game. It only affects two secondary features:
1. The "▶ Running: ..." bar in the main window won't list that game when it's actually running.
2. The auto-check-on-launch feature (`game_detected` signal → pings 5 seconds after a monitored game starts) silently won't fire for that game.

This is the same isolation principle as the four launcher detectors in `game_detector.py` — one broken thing degrades gracefully, it doesn't cascade.

**The fix, generalized into a standing pattern:** `exe` / `exe_mac` / `exe_linux` can now be **either a single string (unchanged for every game except Apex) or a list of accepted aliases**.
- `games.py`: `_as_list()`-aware docstring added explaining the convention. Apex Legends' `exe` is now `["r5apex.exe", "r5apex_dx12.exe"]` — both the original guess and the confirmed-real name, so neither an old install on the older build nor the current one falls out of detection.
- `ping_engine.py`: `get_process_name_for_game()` (singular) replaced with `get_process_names_for_game()` (returns a list). New `_as_list()` helper normalizes string/list/missing into a clean list. `check_running_games()` now checks for *any* overlap between accepted aliases and currently-running processes (`proc_names & running_exes`) instead of one exact string match. The Minecraft special-case carve-out is untouched.
- Confirmed safe to change: `get_process_name_for_game` was only ever called from within `ping_engine.py` itself — renaming it carries no risk to `app.py`/`main_window.py`.
- Custom games added via Add Game still just store a plain string for `exe` — `_as_list()` handles that with zero changes needed there.

**Session 17 confirmation: this all works correctly end to end.** A real live Apex Legends launch correctly populated the "▶ Running" bar and produced real ping history.

**Why this matters for future reports (dev's explicit point, Session 16):** "publisher renamed the exe" is now a *named, known failure mode* with an established one-line fix — add the new name to the list — the same way "blended region fallback" became one in Session 15. A future report that some other game stopped showing as "running" should be checked against this pattern first before debugging from scratch.

---

## Region Separation System — Architecture (Built Session 15)

**The problem:** several `DEFAULT_GAMES` entries blend multiple regions into one game with a fallback endpoint list (e.g. old "Overwatch 2" tried `eu.battle.net` then `us.battle.net`). Confirmed via `ping_engine.py`: a TCP connection that's actively *refused* still counts as a successful ping ("server is reachable, just saying no") — so the first endpoint in a list almost always "succeeds," and any fallback endpoint after it is effectively dead code. Non-EU players were unknowingly having EU latency reported as their own ping.

**Critical architecture fact, easy to miss:** `DEFAULT_GAMES` in `games.py` only matters once — the very first time a user launches the app (`GameManager._reset_to_defaults()`). After that, `games.json` on disk is the real source of truth and `DEFAULT_GAMES` is never consulted again. Any change to `games.py` alone is **silently invisible to every existing install** unless paired with a migration in `settings.py`'s `GameManager.load()`.

**Also critical, and reconfirmed independently by the Session 17 data bug above:** `GameManager.update_ping()`, `remove_game()`, and `update_game()` all match games purely by `game["name"] == name`. The name string **is** the identity of a game in this data model — renaming an entry without a migration orphans its saved history, and (as Session 17 showed) allowing a duplicate name to exist at all silently corrupts data with no warning.

**The fix, built and validated Session 15:**
1. **Standalone entries per region** — same pattern every other game in `games.py` already uses. "Overwatch 2" became `"Overwatch 2 (EU)"` and `"Overwatch 2 (NA)"`, two fully independent entries, each with one endpoint, addable/removable/enableable independently.
2. **`migrate_game_regions()` in `settings.py`** — sibling to the existing `migrate_game_endpoints()`, runs automatically on every `GameManager.load()`. Renames the existing user's saved entry in place to its first region (preserving `ping_history`/`enabled`/`last_ping` exactly), then appends any new region variant fresh, **disabled by default**. Verified directly against a real `games.json`: EU kept its full 60-sample history, NA appeared fresh and disabled, re-running the migration a second time is a safe no-op.
3. **Setup wizard's region step, rebuilt (twice)** — see below.

### Setup wizard rebuild — what actually shipped, and why it took two attempts
- **First attempt:** suggested a region by pinging `eu.battle.net` / `us.battle.net` and auto-picking the faster one. **Confirmed broken by real testing** — from South Africa, NA came back at 7ms, which is physically impossible. Root cause: these Battle.net hostnames' HTTPS front door sits behind a global CDN.
- **Fix, verified before building:** switched to AWS's own per-region service endpoints (`ec2.<region>.amazonaws.com`) — real, fixed, named datacenters, not anycast. Verified directly via the dev's own `tcp_ping()`:

  | Region | AWS location | Hostname | Measured (Cape Town) |
  |---|---|---|---|
  | NA | Virginia | `ec2.us-east-1.amazonaws.com` | 207ms |
  | EU | Ireland | `ec2.eu-west-1.amazonaws.com` | 172ms |
  | Asia | Singapore | `ec2.ap-southeast-1.amazonaws.com` | 312ms |
  | SA | São Paulo | `ec2.sa-east-1.amazonaws.com` | 143ms |
  | OCE | Sydney | `ec2.ap-southeast-2.amazonaws.com` | 369ms |
  | Africa | Cape Town | `ec2.af-south-1.amazonaws.com` | 24ms |

- **Design decision (dev's explicit call):** don't auto-pick-and-hide. Show all six regions as individually selectable rows with real ms displayed, fastest pre-selected but fully overridable.
- **Also fixed:** wizard page order — region now before games, so `_apply_region_aware_checks()` can correctly pre-check only the matching sibling instead of double-checking every regional variant.
- **Confirmed working end to end** via fresh-install testing.

### Explicitly NOT done yet (don't assume otherwise):
- **Call of Duty: Warzone** has the identical `eu.battle.net`-first blended pattern as old Overwatch 2 — held back because its second endpoint is a raw IP (`172.64.155.188`) that might be genuine NA infrastructure or might be Cloudflare anycast; unverified, deliberately not touched yet.
- **The other ~16 games in `DEFAULT_GAMES`** haven't been audited for the same issue.
- **A real per-game region management screen** doesn't exist yet.

---

## Icon Build Process — PingGuard-Specific Notes
Same base technique as StartGuard (gradual shrink + sharpen for small sizes, manual ICO builder via `struct`). PingGuard-specific refinement: thin detail (the crosshair) vanishing at 16px fixed via enlarging the inner target ~1.3x with a soft radial blend mask for the smallest sizes only. Full detail preserved from Session 14.

## Icon Wiring — Confirmed Working (Session 14)
Full chain verified via the actual built `.exe`: title bar, taskbar, tray, and Windows notifications all correct. AppUserModelID set in `main.py` as a defensive layer.

---

## File Inventory

| File | Status | Notes |
|------|--------|-------|
| `main.py` | ✅ Stable | Version `2.1.0`. AppUserModelID set before `QApplication` is created. |
| `app.py` | ✅ Reviewed Session 16, unchanged | Confirmed it never reads `game["exe"]` directly — only consumes `ping_worker.get_running_games()`. |
| `settings.py` | ✅ Updated (Session 17) | `GameManager.add_game()` now checks for an existing name (case-insensitive) before adding; returns `True`/`False` instead of always succeeding silently. Confirmed only one call site exists app-wide. `migrate_game_regions()` + `migrate_game_endpoints()` unchanged. `update_game()` confirmed to exist but have no UI caller anywhere — there is currently no way to edit an existing game's settings after adding it (flagged as a real feature gap, see Open Questions). |
| `main_window.py` | ✅ Updated (Session 17) | `_on_add_game()` now checks `add_game()`'s return value and shows a `QMessageBox.warning` on a duplicate name instead of silently doing nothing. Confirmed it never reads `game["exe"]` directly — purely a display layer for whatever `ping_engine.py` resolves. |
| `games.py` | ✅ Updated (Session 16) | Apex Legends `exe` fixed to `["r5apex.exe", "r5apex_dx12.exe"]`. New module docstring documents the string-or-list convention for `exe`/`exe_mac`/`exe_linux`. Overwatch 2 (EU)/(NA) split unchanged from Session 15. No code changes this session — the duplicate-entry problem found Session 17 was in the user's `games.json` data file and the `add_game()` guard logic, not in this file. |
| `add_game_dialog.py` | ✅ Updated (Session 16), confirmed working Session 17 | Server Address field clarity fix: relabeled, tooltip added, explanatory hint added, dialog height bumped 520→555. Detected-games dropdown, Browse button, game-request report hook all confirmed working correctly via real live testing. |
| `game_detector.py` | ✅ Stable since Session 15 | Steam/Epic/Riot/Battle.net detection. |
| `reporter.py` | ✅ Stable since Session 15 | `send_game_request()` + `send_report()`. |
| `setup_wizard.py` | ✅ Reviewed Session 17, unchanged | Confirmed it does not call `GameManager.add_game()`, so the new return-value contract doesn't affect it. First-run wizard, region step before games step, unchanged from Session 15. |
| `ping_engine.py` | ✅ Updated (Session 16), confirmed working live Session 17 | `get_process_name_for_game()` replaced with `get_process_names_for_game()` (returns a list). New `_as_list()` helper. `check_running_games()` now matches on alias-set overlap instead of one exact string. Confirmed this function had no callers outside this file, so the rename is safe. Minecraft special-case untouched. `tcp_ping()` refused-connection-counts-as-success behavior unchanged from Session 15. A real live Apex Legends launch confirmed correct "Running" detection and ping history. |
| `logger.py` | 🆕 Discovered Session 15, not touched | CSV session logging for ping history, 30-day auto-cleanup. |
| `theme.py` | ✅ Stable | No changes since Session 14. |
| `reporter.py` / `constants.py` / `constants_example.py` | ✅ Stable | Webhook handling unchanged. |
| `pingguard.spec` / `PingGuard.iss` / `requirements.txt` / `.github/workflows/build.yml` / `.gitignore` | ✅ Stable | No changes this session. |

---

## Architecture Decisions — Confirmed
- Webhook lives in `constants.py` only — never settings, never user-configurable ✅
- One source of truth for version — `app.setApplicationVersion()` in `main.py` ✅
- `.iss` paths always `SourcePath`-relative ✅
- Single instance lock port: **47823** (StartGuard uses 47824)
- HTTP calls use `requests` — Discord blocks urllib
- Theme: token-dictionary pattern — standard for all future JackalNode apps
- **Standing pattern (Session 15): regional variants of a game are always standalone, independent entries** — never a blended endpoint list with fallback.
- **Standing pattern (Session 15): `games.json` is the real source of truth once it exists.** Changes to `DEFAULT_GAMES` only affect fresh installs — any structural change needs a paired migration in `settings.py`.
- **Reference data (Session 15): AWS regional endpoints are the trusted target set for any future "which region is closest" testing.**
- **Standing pattern (Session 16): `exe` / `exe_mac` / `exe_linux` can be a single string or a list of accepted aliases.** Use a list whenever a publisher is found to have renamed an executable, so old and new installs both keep matching instead of one stale name silently failing. Established via the Apex Legends `r5apex.exe` → `r5apex_dx12.exe` fix.
- **Architecture fact (Session 16): `exe` matching only ever feeds two secondary features** (the running-game badge, and check-on-launch) — it has no path to the core ping test, which is purely host/port based. Confirmed via direct review of `app.py` and `main_window.py`.
- **New standing pattern (Session 17): a game's name is its sole identity everywhere in this data model, and that is now actually enforced, not just documented.** `GameManager.add_game()` refuses to add a game whose name already exists (case-insensitively), returning `False` instead of silently appending. Any UI calling `add_game()` must check the return value and surface a clear message on failure — never assume success.
- **New architecture fact (Session 17): `update_ping()`'s first-match-wins behavior is only safe because duplicate names are now structurally prevented at the `add_game()` layer.** If that guard is ever removed or bypassed, the silent data-corruption bug found this session (ping results written to the wrong entry, with zero error) returns immediately.
- **Process lesson (Session 17): when an AI agent's summary of file content contradicts something directly observed on screen, ask for the literal raw data, not a re-summarized table.** This caught a backwards conclusion before any data was touched.

---

## Release Sequence — Roadmap

### v2.0.5 / v2.0.6 — Patch: Bug Fixes & Infrastructure Parity ✅ SHIPPED
### v2.1.0 — Icon Completion + Light/Dark Theme + Cleanup ✅ SHIPPED

### v2.2.0 — Minor: Per-Game Management 🟡 IN PROGRESS
*Moderate risk — touches the core data model and monitoring loop.*
- ✅ Add Game auto-detection (Steam/Epic/Riot/Battle.net)
- ✅ Region-separation architecture, migration, and wizard rebuild (Overwatch 2 as worked example)
- ✅ Add Game host-field clarity fix (Session 16)
- ✅ Apex Legends exe mismatch fixed + generalized into exe-alias architecture, confirmed via real live launch (Session 16/17)
- ✅ Duplicate-game-name data corruption bug found, root-caused, and fixed (Session 17) — not originally planned, surfaced during testing
- 🔲 Call of Duty: Warzone region split (pending endpoint verification)
- 🔲 Audit remaining ~16 default games for the same blended-region issue
- 🔲 Audit remaining default games for the same exe-staleness risk (lower priority — only surfaces when a publisher actually renames something)
- 🔲 Real per-game region management screen (enable/disable specific variants post-setup)
- 🔲 Per-game ping thresholds (not started)
- 🔲 Real "edit an existing game" UI (newly flagged Session 17 — `update_game()` already exists in `settings.py` but has no caller anywhere)
- 🔲 Investigate psutil-based live-connection detection to help auto-suggest Server Address for unlisted games (newly flagged Session 17 — see Add Game section)

> COMING SOON: Stop pinging Frankfurt when you're playing on Joburg servers.

### v2.3.0 — Minor (tentative): Game Search
*Only proceeds if a workable data source for game server info is confirmed.*
- Game search when adding a new game, with auto-populated server info
- The psutil live-connection idea above is now the leading candidate direction for this, ahead of a maintained lookup database

### v3.0.0 — Major: Network Diagnostics
*High risk — new engine, new permissions model, new UI surface. Dedicated session(s) only.*
- Traceroute, hop latency, ISP identification, packet loss per hop
- Raw sockets require admin/root on Windows — elevation approach not yet decided

---

## Still To Do / Open Questions
- **Call of Duty: Warzone** region split — needs endpoint verification before splitting (see Region Separation section).
- **Audit the other ~16 default games** for the same blended-region-fallback issue — which are genuinely region-specific vs. already global/anycast.
- **Audit the other ~16 default games for exe staleness** — lower priority than the region audit, but the same "publisher renamed it" risk applies to any game, not just Apex. No known cases yet beyond Apex.
- **Real per-game region management UI** — doesn't exist yet; needed for the "League on EU, CS on local" flexibility the dev wants long-term.
- **Real "edit existing game" UI** — confirmed not to exist anywhere in the app (Session 17). The dev wants both easy add *and* easy remove; `remove_game()` exists but it's worth confirming there's an actual visible button/menu wired to it before assuming removal is solved — not yet checked.
- **Server Address auto-fill for unlisted games** — confirmed there is no way to do this via the four launcher detectors (they only know what's installed, not what it connects to). Investigate using `psutil` to list a running game's active remote connections as a "pick from what it's actually talking to" alternative to typing a guess. Flagged Session 17 as the direction to investigate first, ahead of a maintained lookup database (tentative v2.3.0 idea).
- **macOS / Linux builds** — v2.0.4 had Beta builds but the pipeline only builds Windows now. Needs dedicated session when ready.
- **Confirm workable game-server-info lookup source** before committing v2.3.0 as a real release vs. dropping it.
- **Decide scapy vs. manual raw sockets** for v3.0.0 — affects elevation handling, approach still undecided.
- **Tray icon cosmetic mismatch** — still shows a generic blue circle, not the shield art. Dev's call to leave as-is, low priority.

---

## Session Log
| Session | What Was Done |
|---------|--------------|
| Pre-12 | v2.0.4 shipped. Rough roadmap doc with stale URLs. Manual build process. |
| 12 | Context doc created. URLs confirmed. Feature backlog reconciled. Release sequence locked. |
| 13 | Full infrastructure parity work. GitHub Actions pipeline built. v2.0.5/v2.0.6 shipped. |
| 14 | Icon system completed end to end. Full light/dark theme system built. Dead Reporting tab removed. v2.1.0 shipped. |
| 15 | Add Game overhaul (`game_detector.py`, detected-games dropdown, Browse button, "couldn't find this game" report path). Region separation discovered, designed, and validated via Overwatch 2 as the worked example, with `migrate_game_regions()` in `settings.py`. Setup wizard rebuilt twice (Battle.net CDN false positive → AWS regional endpoints). Newly flagged: Add Game host-field clarity gap, Apex exe mismatch, CoD Warzone region split held back, ~16 games not yet audited. |
| 16 | **Add Game host-field fix:** "Server Host" relabeled "Server Address", tooltip added, explanatory hint added pointing confused users to the report fallback, dialog height bumped 520→555 to fit it safely. **Apex Legends exe fix, generalized:** confirmed via direct review of `app.py`/`main_window.py`/`ping_engine.py` that `exe` matching only ever affects two secondary features (running-game badge, check-on-launch) and never the core ping test. Replaced the single-string exe matcher in `ping_engine.py` with a list-aware one (`get_process_names_for_game()` + `_as_list()` helper). Updated Apex's entry in `games.py` to list both `r5apex.exe` and the confirmed-real `r5apex_dx12.exe`. Documented this as a new standing pattern. Not yet verified against a real Apex launch — flagged as the one open follow-up. |
| 17 | **Claude Code adopted** as the primary hands-on tool for PingGuard — installed, authenticated, and a `CLAUDE.md` generated from this context doc for persistent project memory. **Apex fix confirmed live** via a real launch — "Running" bar and ping history both worked correctly. That test surfaced a **separate, serious bug**: adding "Apex Legends" through Add Game created a duplicate name alongside an old disabled entry already in `games.json`, and `update_ping()`'s first-match-wins behavior was silently writing all real ping data into the wrong (disabled, invisible) entry while the actually-monitored entry stayed empty — with no error or warning anywhere. Root-caused via direct file inspection (not assumption), including catching and correcting a backwards first read from Claude Code by comparing it against what was actually observed on screen. **Fixed properly:** `GameManager.add_game()` now refuses duplicate names (case-insensitive) and returns `True`/`False`; `main_window.py` shows a clear warning on a duplicate instead of silently doing nothing. Confirmed only one call site existed and no edit-game UI exists anywhere, so the warning message was worded accordingly. One-time manual cleanup of the dev's own `games.json` merged the two Apex entries, preserving the real 60-sample ping history, with a backup taken first and the fix applied only after confirming the app process had fully exited. Confirmed working end to end live: Apex shows enabled with history intact, and re-adding it now shows a proper "already in your list" warning. **New idea flagged** for a future session: psutil-based live-connection detection as a way to help auto-suggest Server Address for unlisted games, instead of the user guessing blind. **Decided:** code changes get committed and pushed to GitHub now; the actual version bump → tag → installer → itch.io release stays held until the rest of the v2.2.0 checklist is complete, per the established batching pattern. |
