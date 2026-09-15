# PingGuard — Context Document
> Paste alongside JackalNode_Context.md at the start of any PingGuard session — though as of Session 17, the primary working method has shifted (see Tooling section below).
> Built fresh in Session 12, modeled on StartGuard_Context.md's structure (StartGuard is the blueprint — see master doc Standing Rule #8).
> Last updated: v2.2.3 SHIPPED. Session 24: fixed three real issues surfaced by user reports — GameManager.add_game() now re-enables a previously-disabled default game instead of permanently blocking re-adding it (any of the 21 defaults unchecked in the first-run wizard was stuck forever); the in-app header's generic controller emoji replaced with a real transparent line-art version of PingGuard's own shield/target logo, theme-adaptive in both light and dark; and FFXIV's endpoint replaced from the meaningless global frontier.ffxiv.com status API to the real, WHOIS- and live-verified neolobby06.ffxiv.com:54994 Chaos/EU lobby server. All three committed as separate fixes/upgrade. New open item: ping-all-games-simultaneously concurrency likely causing self-inflicted jitter in readings app-wide, not yet investigated. Session 25: Valorant/LoL's ping display replaced with a real Riot service-status check instead of TCP ping — the direct fix for the Session 19 finding that TCP ping can't measure real match latency for either title. Left unfinished — two confirmed bugs found via live testing, neither root-caused. **Session 26: both bugs fixed and verified live.** Click-to-expand was a deliberate early-return in `GameRow.mousePressEvent()` for status rows — removed. The region bug was `check_riot_status()` reading one hardcoded shard, never `settings.user_region` — fixed with a per-region `status_shards` map, live-verified against Riot's real status endpoints, and the region list expanded from 5 to 8 (added Korea, Brazil, and Africa). See dedicated section below. **Session 27: root-caused and fixed the Session 24 ping-jitter open item.** Two independent live test scripts (135 combined rounds) directly disconfirmed the "unthrottled parallel pinging" theory and instead isolated an OS-level DNS-cache-TTL-expiry cost as the real mechanism. Fixed with a discard-first warm-up ping in `_ping_one()`. Also added, at the dev's request, a full pause of background pinging/notifications while any monitored game is running. Both live-verified. See dedicated section below.

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
- **Established working pattern:** for anything with a side effect — editing a file, running a command that changes state, deleting/merging data — Claude Code shows the exact diff or exact before/after first; the dev (often relaying through this chat) confirms before it's applied. This pattern caught real problems three separate times this session alone (the Apex duplicate-data misread, a stale pre-edit Grep output shown as if it were post-edit, and a buggy first draft of a `settings.py` migration) — it is now a load-bearing part of how this project avoids shipping silent bugs, not just a nice-to-have habit.
- **Standing rule, reconfirmed multiple times this session:** when an agent describes file or code content in prose ("the function does X," "added 1 line removed 1 line," "the fixes dict checks for Y") rather than pasting the literal content, treat that description as unverified until the literal content is actually seen. This applies to summaries of *data* (the Apex `games.json` case) and equally to summaries of *code* (the `migrate_game_endpoints()` case) and to summaries of *tool output* (the stale Grep case) — all three happened this session.
- **Login is account-wide** — once logged in for PingGuard, no second login needed to use Claude Code in the StartGuard folder later.
- Same Pro plan, same usage pool as chat — heavy Claude Code sessions and heavy chat sessions on the same day can compound toward the same limit.

---

## Current State
- **Version:** v2.2.3 shipped and live on both GitHub and itch.io — itch.io was manually updated to current this session, the first time it's matched GitHub since v2.2.0 (the prior itch.io-lag caveat is resolved). v2.3.0 not yet started — see roadmap.
- **Platforms:** Windows (live). macOS / Linux — Beta builds existed in v2.0.4 but not yet rebuilt for production. **macOS Stage A test build completed Session 20** via a new manual GitHub Actions workflow, sent to a real tester — see dedicated section below. "Session 22: now part of the tag-triggered release pipeline — build.yml's build-macos job builds and attaches a real macOS asset to every tagged Release, sequenced after the Windows job (needs: build). Verified via a real v2.2.2 release and confirmed by a real tester. No longer experimental."
- **Live on itch.io** under the JackalNode account, same pricing model as StartGuard ($0 or donate)
- **GitHub Actions pipeline:** ✅ Live and working — tag push → cloud build → installer attached to release automatically
- **Auto-update:** ✅ Wired in via shared `updater.py`
- **Report button:** ✅ Fixed — webhook in `constants.py`, gitignored. Sibling "couldn't find this game" report path also live (see Session 15).
- **Icon:** ✅ Real PingGuard-specific art, confirmed across title bar, taskbar, tray, and Windows notifications.
- **Light/Dark theme:** ✅ Built and shipped — full token-based system, toggle lives in Settings → Appearance, applies live with no restart required.
- **Settings dialog:** dead "Reporting" tab removed entirely — single flat layout now, no tabs.
- **Add Game:** ✅ Auto-detects installed games from Steam, Epic, Riot, and Battle.net (Session 15). ✅ Server Address field clarity fixed (Session 16). ✅ Now refuses duplicate game names with a clear warning instead of silently corrupting data (Session 17).
- **Region separation:** 🟡 Real fixed-regional-address split built and validated for Overwatch 2 only (Session 15). **Call of Duty: Warzone's dead fallback endpoint fixed (Session 17), but this is explicitly NOT a regional split** — see new section below for why that pattern isn't available for Warzone the way it was for Overwatch 2.
- **Process detection (running-game matching):** ✅ Hardened (Session 16), ✅ confirmed working via a real live Apex Legends launch (Session 17).
- **New diagnostic tool, Session 17:** `trace_connections.py` — standalone script (not part of the shipped app) that lists a running game's real active network connections via `psutil`. Built to verify Call of Duty: Warzone's real server address; doubles as a working proof-of-concept for the previously-flagged "psutil-based Server Address auto-fill" idea.

---

## Project & Build Paths
- **Project path:** `E:\Projects\PingGuard v3\PingGuard` — confirmed Session 21 (previously documented path was stale, predating the Session 20 machine reinstall; project lives on a separate physical drive from the OS, which is why it survived that reinstall intact).
- **Local Python install (confirmed Session 21):** `C:\Python314\python.exe`. Note: the master doc (`JackalNode_Context.md`) currently documents a different path (`AppData\Local\Python\pythoncore-3.14-64\python.exe`) — unclear whether that's a second install or simply stale; worth reconciling next time either doc is touched. The `python`/`python3` commands on PATH resolve to the Microsoft Store's alias stub, not a real interpreter, and will error out — always use the `py` launcher or the confirmed direct path above.
- **Local Inno Setup (confirmed Session 21):** was not installed on the dev machine post-Session-20-reinstall — installed fresh via `winget install JRSoftware.InnoSetup` (v6.7.3), landing per-user at `C:\Users\natha\AppData\Local\Programs\Inno Setup 6\ISCC.exe`. Note this differs from the machine-wide path GitHub Actions' cloud runner uses (`C:\Program Files (x86)\Inno Setup 6\ISCC.exe`, hardcoded in `build.yml`) — both are correct for their respective environments, not a conflict, just worth knowing they differ if debugging either locally or in CI.
- **PyInstaller output:** platform-dependent as of Session 21's onedir migration. Windows: `dist\PingGuard\` (folder — `PingGuard.exe` + `_internal\`). macOS: `dist\PingGuard.app` (via the existing darwin `BUNDLE()` step, unchanged). Prior to Session 21, Windows produced a single `dist\PingGuard.exe` file (onefile) — that shape no longer applies.
- **Inno Setup OutputDir:** `installer_output\` (SourcePath-relative)
- **GitHub repo:** `github.com/JackalNode/pingguard`
- **itch.io:** `jackalnode.itch.io/pingguard`
- **Folder structure confirmed (Session 15, via screenshot):** everything sits flat in the project root — no `core/` subfolder. `game_detector.py` lives here too, alongside `games.py`, `reporter.py`, etc. `trace_connections.py` (new, Session 17) also sits flat in the root, but is a standalone research tool — it is not imported by, or part of, the shipped app.
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
- "Installed Games" dropdown above the manual-entry form, populated by `detect_all_games()`. Selecting an entry fills in the Game Name field. **Confirmed working correctly Session 17** via real testing.
- The manual `name_input` field doubles as the "can't find it" fallback — no separate UI mode needed, just a hint label pointing at it.
- **Browse... button** next to Process (.exe) — opens directly to the detected game's install folder so the user picks the real exe instead of typing it. **Confirmed working correctly Session 17.**
- **Report hook:** "🎮 Tell the dev I couldn't find this game" sends the typed name to Discord via `send_game_request()` in `reporter.py` — separate from `send_report()`.
- **Server Address field — fixed Session 16, confirmed working as intended Session 17:** label "Server Address", tooltip, and hint line pointing to the report fallback. **Known remaining limitation:** there is no way to auto-fill this for a game that isn't already in `games.py` — the four launcher detectors only know what's installed, not what server a game talks to. The `trace_connections.py` tool built this session (see below) is a real, working proof-of-concept for solving this via `psutil` live-connection detection — confirmed practical, but noisy (a single real game session showed up to 9 simultaneous connections across CDN/cloud/game-server traffic), so an automated in-dialog version would need real filtering logic, not just a raw connection dump. Still flagged as future design work, not a quick fix.
- **Dialog `setFixedSize`:** 420×555 (bumped from 520 in Session 16 to fit the Server Address hint text).

**Confirmed bug, fixed Session 16, confirmed live Session 17:** Apex Legends' hardcoded `exe` in `DEFAULT_GAMES` was `r5apex.exe`; Browse-detection on the dev's real install found the actual running executable is `r5apex_dx12.exe`. Fixed and generalized into the exe-alias architecture (see Process Detection section).

---

## Data Integrity — Duplicate Game Names Silently Corrupt Ping Data (Discovered & Fixed Session 17)

**How this surfaced:** while live-testing the Apex Legends exe fix, the dev added "Apex Legends" via Add Game to get a fresh entry to test against. This created a **second** "Apex Legends" entry alongside an old, disabled one already sitting in `games.json` from before the Session 16 fix shipped. Nothing in the app warned that the name already existed.

**The actual bug, root-caused via direct file and code inspection:**
- `GameManager.add_game()` in `settings.py` blindly appended the new game dict with **no check for an existing name**.
- `GameManager.update_ping()` matches games by `game["name"] == game_name`, walking the list and **breaking on the first match**. With the old disabled entry sitting earlier in the file than the new enabled one, every real ping result for "Apex Legends" was being written into the **old, disabled entry** — not the new, enabled one actually being pinged.
- **Important process note:** Claude Code's first read of the situation got the two entries backwards — caught only because the dev compared it against a literal screenshot rather than accepting the summary, and asked for raw file content instead of a re-summarized table.
- **Bonus finding, no longer reachable but worth remembering:** `remove_game()` uses a list filter, which would have removed *every* entry sharing that name, including the one with real history — the opposite failure mode from `update_ping()`'s first-match-wins.

**The fix, applied Session 17:**
1. `GameManager.add_game()` now checks case-insensitively whether a game with that exact name already exists before adding. Returns `False`/`True` instead of always succeeding silently.
2. `main_window.py`'s `_on_add_game()` now checks that return value — on `False`, shows a clear `QMessageBox.warning` ("A game named '...' is already in your list.") instead of silently doing nothing.
3. **Confirmed safe before applying:** verified `add_game()` has exactly one call site app-wide, and that no edit-existing-game UI exists anywhere (so the warning wording doesn't reference a feature that doesn't exist).
4. **One-time manual cleanup of the dev's own `games.json`:** the two Apex Legends entries were merged into one, preserving the real 60-sample `ping_history`, with a backup taken first and the edit applied only after confirming the app process had fully exited.
5. **Confirmed working end to end, live:** re-launched the app, Apex showed enabled with its history chart intact. Re-adding "Apex Legends" now shows the new "already in your list" warning instead of a silent no-op.

**Why this matters beyond Apex:** any game name, default or custom, could have hit this exact failure mode. The fix protects every game going forward, not just the one that happened to surface it.

---

## Add Game — Re-Enable Instead Of Block On Disabled Games (Session 24)

**How this surfaced:** real user reports (secondhand, via the dev's own contacts, not filed on Discord/GitHub/itch.io) that people couldn't add games back after removing them. Reproduced live, deliberately: disabled "GTA Online" via a direct one-line edit to the dev's `games.json` (the same effect unchecking it in the first-run wizard has), relaunched — it correctly vanished from the list — then tried to re-add it via "+ Add Game." Got "A game named 'GTA Online' is already in your list," a dead end, exactly matching the reports.

**Root cause, confirmed via literal source, not assumed:** `GameManager.add_game()` (Session 17's duplicate-name fix) checks for a name match against `self._games` — the full list, including disabled entries — and returns `False` unconditionally on any match. But `enabled: False` is only ever set in one place in the whole app: the first-run `setup_wizard.py` checklist. There is no "Manage Games" screen, no toggle, no re-enable path anywhere else. So any of the 21 defaults a user unchecked during onboarding becomes permanently stuck: hidden from the list forever (`main_window.py`'s `_populate_games()` skips disabled entries), and permanently unaddable (`add_game()` sees it "already exists" and refuses). Given the wizard's entire purpose is "uncheck the games you don't play," this likely affects a large share of first-run users, not an edge case.

**The fix:** `GameManager.add_game()` now re-enables the existing disabled entry (reusing its known-good endpoint/exe data, since disabled entries only ever come from `DEFAULT_GAMES` and already have correct data) instead of rejecting the add. A name match against a still-*enabled* game is unchanged — still correctly blocked as a real duplicate.

**Verified live, full regression pass:** re-adding a disabled default game re-enables it with zero data loss (confirmed by reading the actual `games.json` afterward — original `endpoints`/`ping_history` intact, not overwritten by whatever placeholder was typed into the Add Game form); case-insensitive re-add works the same way; a genuinely-enabled duplicate still throws the warning; a brand-new custom game still adds normally.

**Known residual friction, not fixed this session:** the Add Game form still requires *something* typed into Server Address before the button will submit at all, even though that value gets discarded when re-enabling a known default game. Minor, not blocking, flagged for whenever the dialog gets touched again.

---

## Call of Duty: Warzone — Endpoint Investigation & Fix (Session 17)

**Starting point:** Warzone's `DEFAULT_GAMES` entry blended `eu.battle.net:443` with a second fallback, `172.64.155.188:3074`, of unconfirmed origin — flagged back in Session 15 as "might be genuine NA infrastructure or might be Cloudflare anycast," and deliberately left untouched until verified.

**Step 1 — the fallback was confirmed dead, not just unconfirmed.** Cloudflare's own published documentation states they use `172.64.0.0/13` (172.64.0.0–172.71.255.255) as public egress IP space. `172.64.155.188` falls squarely inside that range. This is the same class of false positive as the original Battle.net-CDN issue that broke the first setup-wizard attempt back in Session 15 — an address that looks regional but is actually anycast, routed to whichever Cloudflare edge is nearest the person pinging it.

**Step 2 — no public source gave a real replacement.** Searched for Call of Duty's actual matchmaking server infrastructure. The publicly available data (Akamai/CloudFront CDN edge nodes from Netify's domain database) is all website/store/stats traffic, not the dynamic matchmaking servers a real match connects to. Important architecture fact uncovered here: **Call of Duty's actual game servers run on Demonware (Activision's own networking subsidiary), architecturally separate from Battle.net.** Battle.net is only the PC login/launcher layer for Activision titles — unlike genuine Blizzard games (Overwatch, Diablo, WoW), where Battle.net *is* the real backend. This means even the existing `eu.battle.net` endpoint in Warzone's entry may only be measuring login-service latency, not real in-match server latency — a deeper question than just "the fallback is fake," noted here but not yet resolved.

**Step 3 — built a real verification tool instead of guessing again.** New standalone script, `trace_connections.py` (not part of the shipped app — a throwaway research tool, same folder as everything else). Uses `psutil` to list every remote address a named running process currently has an open connection to. Handles both old (`Process.connections()`) and new (`Process.net_connections()`) psutil API names automatically, since the installed version on the dev's machine wasn't known in advance.

**Step 4 — real data captured from a live Warzone match.** Running it repeatedly during an actual match surfaced these distinct remote addresses (consolidated across runs):
- `2.20.13.x:80` — Akamai CDN range, varying last octet (classic CDN load-balancing behavior)
- `99.83.136.34:443` / `18.185.25.14:443` — AWS ranges, both `CLOSE_WAIT` (already-closing, not live gameplay traffic)
- `23.11.207.111:443`, `23.192.228.147:80` — Akamai again
- `172.64.146.157:443` — **another address inside the same Cloudflare `/13` block already identified as fake** — confirms that range shows up repeatedly in this game's traffic for non-gameplay purposes (store/API), reinforcing that the original fallback being Cloudflare was no coincidence
- `34.117.196.76:443` — Google Cloud Platform range
- `35.204.122.188:1119` — also GCP-range, but **port 1119 is notable**: it's the same port already used as the "real game-server" port for World of Warcraft's second endpoint elsewhere in `games.py` — flagged as worth a closer look in a future session, not resolved now
- **`185.34.106.103:3074`** — appeared in **every single run**, status `ESTABLISHED` (a TCP-specific state, confirming this is reachable the same way PingGuard's own `tcp_ping()` works), and not on a typical web port

**Step 5 — verified ownership before trusting it.** WHOIS lookup confirmed `185.34.106.0/24` is officially registered to **Demonware Limited** — Activision's own networking subsidiary — not a CDN, not a cloud provider, not anycast. This is the real thing, confirmed via authoritative registry data rather than inferred from a third-party blog.

**Step 6 — verified it actually works the way PingGuard pings things.** Ran the real `tcp_ping()` function (the exact one in `ping_engine.py`, not a stand-in) against `185.34.106.103:3074` from the dev's machine in Cape Town: **248ms, successful, no error.** A high number here is the correct sign, not a concerning one — genuine distant datacenter infrastructure should read high from far away; a suspiciously low number (like the impossible 7ms the original Battle.net CDN front door gave during Session 15's wizard testing) is what would have indicated another fake/anycast address.

**Important scope limitation — read carefully before assuming this is "Warzone's NA server" or similar:** Demonware does not appear to expose a small set of fixed, named regional addresses the way Battle.net does for genuine Blizzard titles. Matchmaking dynamically assigns players to whichever datacenter it picks, which can vary session to session. So this fix is **not** the same shape as the Overwatch 2 region split — there is currently no second, alternate, confirmed-real regional address to split into. What was actually fixed is narrower and fully justified by evidence: the known-dead Cloudflare fallback was replaced with a confirmed-real, confirmed-reachable Demonware address. `eu.battle.net` was left untouched. No EU/NA split was attempted, because the addresses needed for that don't currently exist in confirmed form.

**The fix, applied Session 17:**
1. `games.py`: Warzone's second endpoint changed from `172.64.155.188:3074` to `185.34.106.103:3074`. One line. Everything else in the entry (name, exe, icon, category, the `eu.battle.net` endpoint, region_note) untouched.
2. `settings.py`'s `migrate_game_endpoints()` updated so existing installs (which already have the dead Cloudflare IP baked into their saved `games.json`) get corrected too — `DEFAULT_GAMES` changes alone never reach existing installs, per the standing rule established in Session 15.

**Two real bugs caught in the first proposed migration diff, before anything was applied — neither was hypothetical:**
1. **The staleness trigger wouldn't have fired at all.** The existing function's check was `h.startswith('185.') or h.startswith('146.')` — written for CS2/Dota2's old bad IPs, which happen to start with those digits. Warzone's actual bad value, `172.64.155.188`, matches neither prefix. Adding Warzone to the dict without changing this check would have silently done nothing on every real user's file.
2. **`region_note` was hardcoded to `'Steam servers'` for every matched game, unconditionally.** Invisible until now because CS2 and Dota2 both genuinely want that label — but plugging Warzone into the same code path unchanged would have correctly fixed its endpoints and then mislabeled it "Steam servers" instead of "EU servers."

**Both fixed by restructuring `fixes` so each game owns its own `is_stale` lambda and its own `region_note`, instead of one shared condition and one shared label for every entry in the dict.** A second issue was caught even in the corrected version before it was applied: Warzone's new correct address, `185.34.106.103`, itself starts with `185.` — meaning a shared/broad staleness check would have kept "fixing" an already-correct Warzone entry forever, causing an unnecessary file save on every single app launch indefinitely (harmless, but pointless, and a sign the underlying logic was still wrong). Resolved by giving each game in `fixes` its own private `is_stale` check (`CS2`/`Dota 2` keep their existing prefix check unchanged; Warzone gets an exact match on `'172.64.155.188' in hosts`, which naturally stops firing once corrected).

**Confirmed before applying, not assumed:** read the literal code of `GameManager.load()` directly — confirmed `migrate_game_endpoints()` runs unconditionally on every load, its return value is OR'd together with `migrate_game_regions()`'s, and `self.save()` fires exactly once if either reported a change.

**Process notes worth remembering on top of the Apex one earlier this session:**
- Claude Code's status line claimed "Added 1 line, removed 1 line" for the `games.py` edit, but the code it printed alongside that claim showed three endpoints, including the supposedly-removed one. Caught by comparing the claim against the literal printed content rather than trusting the summary. Re-reading the file fresh confirmed the edit had actually applied correctly — the mismatch was stale pre-edit Grep output being shown, not a real bug — but the lesson stands regardless of which side turned out to be right: the claim and the literal content disagreed, and that's the trigger to re-check, not to guess which one is correct.
- A description of `migrate_game_endpoints()`'s behavior ("the fixes dict checks for stale IPs using a prefix filter") was offered in place of the literal source code. Demanding the actual source surfaced the two real bugs above. A description of correct-sounding behavior is not the same as correct behavior.

## Apex Legends — Endpoint Investigation & Fix (Session 18)

**Starting point:** Apex's `DEFAULT_GAMES` entry blended `eaassets-a.akamaihd.net:443` (Akamai CDN) with `159.153.64.1:37015`, flagged in the Session 17 audit list as needing the same WHOIS-verification treatment as Warzone.

**Step 1 — confirmed via literal code that `ping_game()` is first-success-wins.** Read directly from `ping_engine.py`: it walks the endpoints list in order and returns on the first success, never trying the rest. Combined with the already-established fact that TCP refusals count as success, this meant Apex's displayed ping was very likely measuring Akamai CDN latency the entire time, not the game server — independent of which second address was "correct."

**Step 2 — live trace via `trace_connections.py` during a real match.** 5 runs surfaced 5 consistent remote addresses, all `ESTABLISHED`. The standout: `100.50.20.250:9000` — the only non-443 connection, present in every run.

**Step 3 — WHOIS-verified both candidates.**
- `159.153.64.1` → genuine direct ARIN allocation registered to Electronic Arts, Inc. Not fake, unlike Warzone's old fallback — but it never appeared in any of the 5 live runs, and timed out on a real `tcp_ping()` call. Left as an open question rather than declared dead: port 37015 is consistent with a UDP-only game-data port, which would explain both the timeout and its absence from a TCP-connection trace regardless of whether the server is actually retired.
- `100.50.20.250` → AWS, `AMAZON-IAD` (Amazon Data Services Northern Virginia). Verified with real `tcp_ping()`: **209ms, successful** — a sane distance-appropriate number for Virginia from Cape Town.

**The fix, applied Session 18:**
1. `games.py`: Apex's `endpoints` replaced entirely with the single confirmed-live entry, `{"host": "100.50.20.250", "port": 9000}`. `region_note` corrected from the stale `"EU servers"` to `"EA servers (US-East, AWS)"`. Akamai CDN and the old EA IP both removed rather than kept as a "fallback" — a fallback that almost always wins isn't protecting anything, it just reintroduces the same shadowing bug.
2. `settings.py`'s `migrate_game_endpoints()`: new `'Apex Legends'` entry added following the established per-game pattern (own `is_stale`, own `region_note`). Collision-checked against CS2/Dota2's `185./146.` prefix check and Warzone's exact-match check — confirmed no overlap in either direction before applying.
3. Both diffs reviewed literally before being applied, including a manual unwrap-and-reread of the `is_stale` lambda after a terminal-width line wrap looked suspicious — confirmed syntactically complete, no truncation.

**Step 4 — live verification surfaced a bigger finding than the fix itself.** Relaunched the app and got into a live match. PingGuard reported `208ms` against the new AWS Virginia endpoint. The in-game data center readout (visible in the Apex settings screen) showed `sa-east-1 (172ms)` — São Paulo, a different continent entirely from the endpoint PingGuard had just verified and shipped.

**Root cause: not a bad fix — a confirmation that Apex's matchmaking dynamically assigns datacenters per match,** the exact same architectural pattern already flagged (but not yet directly observed) for Warzone's Demonware backend. The captured AWS address was genuinely correct for the match it was captured during; it simply can't follow the player to a different datacenter on a later match. This elevates the "dynamic datacenter assignment" risk from a Call-of-Duty-specific footnote to a confirmed, generalizable limitation likely to affect any title using cloud-hosted, matchmaking-assigned dedicated servers — worth assuming by default on the remaining un-audited games, not just checking for case by case.

**Decision: ship as-is, document the limitation, don't chase further in v2.2.0.** The fix is still a strict improvement (no more CDN-shadowed number masking the real issue), and will read correctly any time a match happens to land in `us-east-1`. Solving the underlying problem properly means real-time per-match server detection — already on the v3 roadmap, and now backed by direct evidence rather than a hunch.

## Path of Exile — Endpoint Investigation & Fix (Session 18)

**Starting point:** Path of Exile's `DEFAULT_GAMES` entry blended `www.pathofexile.com:443` with `45.33.26.109:20481`, flagged in the original audit list (alongside World of Warcraft) as needing the same WHOIS-verification treatment as Warzone and Apex.

**Step 1 — process name correction needed before tracing.** The hardcoded `exe` value, `"PathOfExile.exe"`, did not match the actual running process. Checked directly in Task Manager: the real process is `PathOfExileSteam.exe`. Same shape of bug as Apex's `r5apex.exe` vs `r5apex_dx12.exe` mismatch from Session 16.

**Step 2 — live trace via `trace_connections.py` during a real session.** 5 runs (run back-to-back rather than with the originally-planned delay, due to a sandbox restriction blocking `sleep` — didn't affect the result, since both connections were already fully stable). Exactly two connections, both `ESTABLISHED`, in every single run:
- `34.144.246.52:6112` — non-standard port, present every run.
- `2.16.199.16:443` — standard HTTPS port, present every run.

**Step 3 — screenshots of PoE's own in-game gateway list provided real ground-truth data, a first for this session's audits.** Unlike Warzone and Apex, where matchmaking dynamically assigns servers, PoE lets players manually pick a fixed gateway from a list, and that choice persists rather than changing per-session. The screenshots showed "South Africa" selected at **22ms** — a genuine, stable, comparable number, not a one-off sample from a single match.

**Step 4 — WHOIS-verified both candidates.**
- `34.144.246.52` → Google LLC (`GOOGL-2`), block `34.128.0.0/10`, explicitly marked in the registration remarks as in use by Google Cloud customers.
- `2.16.199.16` → Akamai Technologies (`AKAMAI-PA`), block `2.16.192.0/20`. Confirms this is the same CDN-shadowing pattern as Apex — almost certainly what `www.pathofexile.com` resolves to, sitting first in the old endpoint list and winning every ping via `ping_game()`'s first-success-wins logic, the same way Akamai shadowed Apex's real server.

**Step 5 — verified against two independent ground-truth numbers, not just one.** Real `tcp_ping()` against `34.144.246.52:6112` returned **32ms** — a 10ms gap against the in-game screenshot's 22ms, attributed to PingGuard's TCP SYN measurement vs. the game's own UDP-based reading. Later, after the fix was applied and the app relaunched, live in-app testing showed PingGuard reporting **27ms** against an actual in-game lobby reading of **32ms** — a 5ms gap. Both independent checks landed in the same tight neighborhood as the in-game numbers — the closest confirmation margin of any endpoint fix this session.

**Architectural note — PoE doesn't share Warzone/Apex's dynamic-datacenter problem.** Because the gateway is a manual, persistent player choice rather than matchmaking-assigned, PoE is a real candidate for an Overwatch-2-style regional split in the future (multiple fixed, named gateways, same as Battle.net's EU/NA pattern) rather than the "best single guess" treatment Warzone and Apex got. Not pursued tonight — would require tracing once per gateway the player manually switches to — but flagged as a stronger fit for the regional-split pattern than anything else audited so far.

**The fix, applied Session 18:**
1. `games.py`: Path of Exile's `endpoints` replaced entirely with the single confirmed-live entry, `{"host": "34.144.246.52", "port": 6112}`. `region_note` corrected from `"EU servers"` to `"South Africa servers (Google Cloud)"`. `exe` changed from the single string `"PathOfExile.exe"` to the list `["PathOfExile.exe", "PathOfExileSteam.exe"]` — the original string kept as one alias rather than removed, in case other distribution channels still use it.
2. `settings.py`'s `migrate_game_endpoints()`: new `'Path of Exile'` entry added following the established per-game pattern (own `is_stale`, own `region_note`), plus a new optional `'exe'` key on the fix dict.
3. **New capability built this session: `migrate_game_endpoints()`'s apply loop extended to also write an `exe` field when present on a fix.** Before tonight, the function only ever wrote `endpoints` and `region_note` — confirmed directly from the literal source before any edit was made. This is a structural change to shared function behavior, not just a new per-game data entry, so it was reviewed separately from the data addition: a single `if 'exe' in fix: game['exe'] = fix['exe']` line, guarded so it only fires for fix entries that actually define an `'exe'` key — CS2, Dota2, Warzone, and Apex's existing entries have no such key, so they're provably unaffected.
4. Collision-checked PoE's `is_stale` (`'www.pathofexile.com' in hosts or '45.33.26.109' in hosts`) against all four existing fix entries before applying — no overlap in either direction.

**Verification rigor, worth noting:** the diff Claude Code first presented for the `games.py` change appeared to show both the old and new `exe`/`region_note`/`endpoints` lines coexisting, with no clean removal. A fresh, direct read of the literal file content immediately after confirmed the actual on-disk entry was correct all along — one `exe` key, one `region_note`, one endpoint — so the conflicting appearance was a rendering artifact, not a real double-write. Caught and resolved the same way as an earlier incident this session (the `is_stale` lambda's apparent bracket/length mismatch, also resolved by checking computed `len()`/ordinal values rather than trusting a pasted description).

---

## World of Warcraft — Endpoint Investigation (Session 19, inconclusive — held open)

**Starting point:** `eu.actual.battle.net:1119`, flagged as the next audit candidate after Warzone/Apex/PoE.

**Step 1 — DNS resolution.** `eu.actual.battle.net` resolves to `34.141.148.228` — Google Cloud, europe-west4 (Netherlands), confirmed via ip-api.com (`AS396982 Google LLC`).

**Step 2 — interpretation, deliberately left open.** Unlike Warzone's confirmed-dead Cloudflare anycast address, a Google Cloud-owned IP is not in itself evidence of a fake/CDN-shadowed endpoint — Path of Exile's real, live-trace-confirmed server (`34.144.246.52`) is also Google Cloud. Ownership data alone cannot distinguish "Blizzard's real backend, cloud-hosted" from "login/launcher-layer front only." That distinction requires a live trace + `tcp_ping()` cross-check against an in-game reading, the same method that confirmed PoE — and that step is currently blocked: the dev does not hold an active WoW or WoW Classic subscription.

**Blocker, explicitly not worked around:** no subscription bypass, account-sharing, or similar was attempted or considered — out of scope regardless of feasibility.

**Decision:**
- **Retail WoW** has a genuine no-cost path forward: Blizzard's official free trial (Starter Edition, levels 1–20) connects to real backend infrastructure and could be live-traced the same way as PoE, at zero cost, whenever there's time for it. Not done this session.
- **WoW Classic** has no equivalent free-trial path (explicitly excluded from the free trial offering) and no live-verification route exists right now.
- **Decision: ship v2.2.0 with `eu.actual.battle.net:1119` unchanged**, documented as unverified rather than confirmed-correct, and lean on the existing Discord error-report path to surface real-world mismatches from players over time, rather than holding the release on a check that can't currently be performed. Revisit if/when retail trial testing happens, a Classic-subscribed tester becomes available, or a future Blizzard free-access weekend opens the door.

**Open question carried forward:** whether `games.py`'s single "World of Warcraft" entry should eventually split into separate retail/Classic entries, since they share a front-door hostname but very likely diverge at the real realm-server level — not resolved, not urgent, flagged for whenever live data becomes available.

---

## Valorant — Endpoint Investigation (Session 19, architecturally blocked)

**Starting point:** `euw1.pvp.net:443` + `eu.api.riotgames.com:443` — both look like account/API layer, not match servers.

**Live trace (2 sessions, 5 runs total) showed only TCP 443 + one stable 5223 (XMPP/presence).** Cross-checked against Riot's own published port requirements: Valorant's real-time gameplay data runs on UDP 7000–8000; every TCP port observed (443, 2099, 5222-5223, 8393-8400) is login/patcher/presence/anti-cheat, never gameplay.

**Root cause confirmed via raw `netstat` output, not inferred:** Valorant's two open UDP sockets both show `*:*` as the remote address in the OS's own connection table — meaning the client uses unconnected (`sendto()`-style) UDP rather than a `connect()`-locked socket. The real server address never gets recorded by the OS at all, so it's invisible to any connection-table-based tool, `trace_connections.py` included. This is not a permissions or Vanguard issue — confirmed directly via `netstat`, independent of `psutil`.

**Decision: ship Valorant's existing endpoints unchanged**, documented as measuring login/API latency only, not real match latency. Closing this with a real root cause rather than a guess. Solving it properly would require packet-level capture (Wireshark or similar) — flagged as a new, separate future investigation, not pursued this session.

**New architecture fact, third class of audit-blocking issue found this project:** unconnected/`sendto()`-style UDP sockets are invisible to any OS-connection-table tool, full stop — distinct from CDN-shadowing (fixable) and dynamic-datacenter-assignment (a real address exists, just changes per session). Worth checking for early on any remaining game with real-time UDP netcode — a quick look at `netstat`'s UDP remote-address column tells you immediately whether this ceiling applies, before investing in a full WHOIS pass.

---

## CS2 — Endpoint Investigation (Session 19, architecturally blocked — Steam Datagram Relay)

**Starting point:** `steamcommunity.com:443` + `api.steampowered.com:443`, region_note "Steam servers" — already honestly labeled as account/API layer, not a claim of measuring real match latency.

**Live trace via raw `netstat`** during a live official matchmaking Deathmatch (not a community server — confirmed via the in-game Play menu, not the Community Servers browser) showed 53 UDP sockets, all unconnected (`*:*` remote address), zero TCP. Same OS-level fingerprint as Valorant, but at much larger scale — Valorant showed 2 unconnected UDP sockets, CS2 showed 53.

**Root cause identified, more specific than Valorant's:** Valve's CS2 client routes all match traffic through Steam Datagram Relay (SDR), a relay network Valve operates specifically so that game-server IP addresses are never revealed to clients — confirmed via Valve's own public SDR documentation. Before matchmaking completes, the client fans out UDP probes across SDR's 49+ worldwide relay points of presence to measure latency to each, which explains the high socket count. Once connected, the address used isn't even a conventional IP — Valve's own discussion threads confirm SDR connections display as an internal token format (`[A:n:nnnnnnnn]`), not an IP:port.

**This is a stronger, by-design version of the same wall Valorant hit** — not just "the OS doesn't happen to record a peer," but "no client-visible server IP exists at all, intentionally, as an anti-DDoS measure." Even Valve's own official diagnostic (`net_print_sdr_ping_times`, an in-game console command showing real ping to every relay) couldn't help PingGuard here — it's UDP-only and console-internal, not something an external app can read, and PingGuard's `tcp_ping()` couldn't measure a UDP relay regardless.

**Decision: ship CS2's existing endpoints unchanged.** Unlike Warzone's old fallback, there's nothing to actually fix — the existing `region_note` never claimed to measure real match latency in the first place. Documenting the real reason rather than leaving it unexplained.

---

## Dota 2 — Endpoint Status (Session 19, inferred — not directly traced)

**Starting point:** `steamcommunity.com:443` + `api.steampowered.com:443`, region_note "Steam servers" — identical endpoint pattern to CS2's pre-audit entry.

**Not live-traced this session — the dev doesn't own Dota 2.** Decision made to document this one by architectural inference rather than spend a session acquiring and trace-testing a game that isn't actually played: Dota 2 is built on the same Valve/Steamworks foundation as CS2, and Valve's own SDR rollout documentation confirms the relay protocol was already in active use on Dota for roughly a year before being extended to all of CS:GO — meaning Dota 2 was SDR's original proving ground, not a later addition.

**Decision: ship Dota 2's existing endpoints unchanged, same reasoning as CS2, on inferred rather than directly-confirmed grounds.** Flagged explicitly as a lower evidence tier than every other audit this session — if a Dota-2-playing tester ever becomes available, worth a real trace to convert this from inferred to confirmed, but not blocking anything in the meantime since the existing endpoint already only claims to be "Steam servers," same honest framing as CS2.

---

## League of Legends — Endpoint Investigation (Session 19, architecturally blocked)

**Starting point:** `euw1.api.riotgames.com:443` + `eu.api.riotgames.com:443`, region_note "EUW".

**Live trace via `netstat`, confirmed during an active ARAM match.** League of Legends runs as two separate processes: `LeagueClient.exe` (the lobby/launcher shell) and `League of Legends.exe` (the actual in-match game process) — confirmed distinct PIDs.

**`LeagueClient.exe`'s external connections (all TCP):** two Cloudflare addresses on port 443 (account/CDN layer), one AWS Frankfurt address on port 2099 (Riot's chat/presence service — the same RTMPS-family port already seen in Valorant's port documentation earlier this session).

**`League of Legends.exe`'s connections:** zero external TCP. One unconnected UDP socket (`*:*` remote address) — identical fingerprint to Valorant's real match-traffic socket.

**Conclusion: this is the same architectural wall Valorant hit, now confirmed on a second, much older Riot title with a completely different game engine and client architecture.** This upgrades the finding from "Valorant happens to do this" to "Riot does this as a company pattern" — worth assuming by default for any remaining Riot title.

**Decision: ship League of Legends's existing endpoints unchanged**, documented as measuring account/API/chat latency only, not real match latency.

**Resolved, same session:** both Valorant's and LoL's `region_note` values were corrected to "Riot account/API layer (not match server)" via a new `region_note_stale` migration entry in `settings.py` (separate from the existing `is_stale` mechanism, so the other 5 entries are unaffected). Applied to `games.py` for fresh installs and confirmed firing correctly on the dev's existing `games.json`.

---

## Desk Audit — 11 Remaining Default Games (Session 19 Follow-up)

**Method:** DNS resolution + IP ownership lookup only — no live trace, no code changes. Same treatment as World of Warcraft's Session 19 audit. The dev doesn't currently own/have access to any of these 11 titles for live testing.

**Findings, one block per game:**

- **Fortnite** — `account-public-service-prod.ol.epicgames.com` resolves to AWS EC2 (us-east-1, plausibly genuine Epic infra, unverified without live trace). `fortnite-public-service-prod11.ol.epicgames.com` resolves to Cloudflare (CDN-shadowed). First endpoint wins via first-success-wins, so the practical result is plausible but unverified. `region_note` ("Epic EU") is wrong regardless — neither endpoint is EU.
- **PUBG** — single endpoint (`prod-live-front.playbattlegrounds.com`) resolves to Akamai. CDN-shadowed, no fallback available.
- **Final Fantasy XIV** — `frontier.ffxiv.com` resolves to a Square Enix-owned IP in Japan but is NOT a regional gateway — confirmed via third-party technical docs that it's a global launcher status-check API used identically by every region's client. `patch-bootver.ffxiv.com` is Akamai CDN (patch delivery, expected). **Follow-up finding:** FFXIV has genuine named per-datacenter lobby servers — `neolobby06.ffxiv.com` for the Chaos (EU) data center specifically, confirmed via community server-monitoring sources showing a stable cluster of IPs (80.239.145.79–89) at consistent ~120ms, distinct from Tokyo-based `frontier.ffxiv.com`. Elevates FFXIV to a stronger regional-split candidate than originally scoped, closer in shape to Path of Exile's gateway-list pattern. NOT yet WHOIS-confirmed or live-trace-verified. No code change applied.
- **Diablo IV** — `eu.battle.net` resolves to AWS Global Accelerator (anycast), same result already seen for Warzone/WoW/Overwatch 2. No new finding.
- **FIFA / EA FC** — `ea.com` is Akamai CDN. `api2.ea.com` is **NXDOMAIN — confirmed dead, doesn't exist.** Currently silent only because `ea.com` wins first via the refusal-counts-as-success behavior. Flagged as a standalone fix, independent of the regional-audit question.
- **Rocket League** — same two Epic hostnames as Fortnite, **listed in the opposite order.** Cloudflare CDN comes first here and wins, where Fortnite's AWS endpoint comes first and wins. Same underlying infra pair, opposite practical outcome — a pure list-order effect.
- **Minecraft** — both endpoints resolve to the identical Microsoft-owned IP (Azure). Genuine first-party cloud infra, not CDN-shadowed. Open question, not a bug: vanilla Java multiplayer doesn't have one central "match server" the way other titles here do — worth discussing whether pinging the session/auth endpoint is even the right model for this title.
- **GTA Online** — single endpoint (`prod.cloud.rockstargames.com`) resolves to Akamai despite the "cloud" name. CDN-shadowed, no fallback.
- **Rainbow Six Siege** — `uplaypc-s-ubisoft.cdn.ubi.com` (literal "cdn" in hostname) resolves to Akamai and wins first. `public-ubiservices.ubi.com` resolves to AWS Global Accelerator, never reached. Same list-order pattern as Fortnite/Rocket League.
- **Destiny 2** — single endpoint (`www.bungie.net`) resolves to Cloudflare. CDN-shadowed, no fallback — "www" is the public site, not a game server.
- **Lost Ark** — `api.amazon.com` resolves to genuine Amazon-owned infra (us-east-1), correct owner (Amazon Games publishes the western release) but wrong region — `region_note` says "Amazon EU."

**No code changes applied.** All 11 ship unchanged this session, same as WoW's treatment — documented as unverified/CDN-shadowed/dead where applicable, pending either live-trace access or the report-system feature below.

---

## Final Fantasy XIV — Endpoint Investigation & Fix (Session 24)

**Starting point:** the Session 19 follow-up desk audit's `neolobby06.ffxiv.com` lead — flagged as a stronger regional-split candidate than originally scoped, but explicitly not yet WHOIS-confirmed or live-trace-verified. `frontier.ffxiv.com` (current endpoint) already confirmed to be a global Japan-hosted launcher status API, not a regional gateway.

**Step 1 — WHOIS-confirmed the lead, closing the gap the Session 19 audit left open.** `neolobby06.ffxiv.com` resolves to `80.239.145.6` — hosted via Arelion Sweden AB (AS1299), physically in Frankfurt, and directly attributed to **Square Enix CO LTD** by IPinfo's registry data. Cross-checked against `neolobby02.ffxiv.com` (the NA equivalent) for sanity: resolves to a completely different owner/location (NTT America, San Jose) — confirms the `neolobbyNN` naming genuinely maps to distinct per-datacenter servers, not cosmetic hostnames pointing at shared infra.

**Step 2 — found the real port via Square Enix's own documentation**, rather than guessing 443 (which `frontier.ffxiv.com` uses only for its unrelated status-check role). Official support docs list FFXIV's real game-traffic TCP ports as 54992-54994, 55006-55007, 55021-55040.

**Step 3 — live-verified, no active subscription required.** A raw TCP reachability test doesn't need a logged-in game session, only authenticating past the lobby does. `Test-NetConnection -Port 54994` succeeded. Port-scanning all five documented ports found only 54994 actually responds — the other four (54992, 54993, 55006, 55007) silently drop the connection (21-second hangs, not a fast refusal) rather than refuse it, meaning most of the documented range isn't open to arbitrary external connections at all, only 54994.

**Step 4 — cross-checked against a clean ICMP baseline before trusting the port's timing.** `ping neolobby06.ffxiv.com` returned 161-162ms across 10/10 packets, zero loss — confirms the underlying network path is genuinely stable. Isolated, sequential TCP-connect timing against port 54994 alone matched almost exactly (158-166ms, an 8ms spread). This matters because the *in-app* reading during this same investigation swung 159-818ms on the identical endpoint — ruling out the endpoint/port choice as the cause of that instability and pointing instead at `ping_engine.py`'s fully-parallel all-games-at-once ping design (see new Still To Do item). The port itself is solid; something about hitting it (and everything else) simultaneously every cycle isn't.

**The fix:**
1. `games.py`: FFXIV's `endpoints` replaced entirely with the single confirmed-live entry, `{"host": "neolobby06.ffxiv.com", "port": 54994}` — `frontier.ffxiv.com` and `patch-bootver.ffxiv.com` both removed rather than kept as fallbacks, since `ping_game()`'s first-success-wins behavior means keeping either one in the list at all (in any order) risks the exact same list-order shadowing bug already documented for Fortnite/Rocket League/R6 Siege — `frontier.ffxiv.com:443` would almost always "win" the race and the real fix would never actually get used. `region_note` corrected to `"Square Enix EU (Chaos DC, Frankfurt)"`.
2. `settings.py`'s `migrate_game_endpoints()`: new `'Final Fantasy XIV'` entry added following the established per-game pattern (own `is_stale`, own `region_note`), so existing installs pick up the fix automatically on next launch — confirmed firing correctly against the dev's own `games.json`.

**Evidence tier: stronger than every prior desk-only audit in this project (Fortnite, PUBG, WoW), on par with the live-traced fixes (Warzone, Apex, PoE) despite no active subscription.** WHOIS ownership attribution (not just generic cloud-hosting ambiguity, per WoW's Google Cloud case), Square Enix's own official port documentation, a live reachability test on the real port, and an independent ICMP cross-check together substitute for the in-game trace a subscription would normally provide.

---

## macOS Stage A Test Build (Session 20)

**Goal:** get a real, launchable `.app` onto a tester's Mac to start closing the macOS gap that's existed since the pipeline went Windows-only. Deliberately scoped as Stage A only — confirm the app packages and launches on real hardware — not a full feature-parity or App Store pass.

**Three fixes applied, in sequence, to make the build possible:**

1. **`game_detector.py` — `winreg` import guard corrected.** The Windows registry module (`winreg`) doesn't exist on macOS/Linux at all — attempting to import it unconditionally crashes at module-load time on any non-Windows platform. The fix moved the platform check to before *any* unguarded reference to `winreg`, not just wrapping the `import` statement itself. An import-only guard (e.g. a bare `try/except ImportError` around just the `import winreg` line) would still crash if any code path later referenced the name directly without re-checking platform — the actual fix checks platform once and gates every reference behind it.

2. **`pingguard.spec` — darwin-only `BUNDLE()` block added.** PyInstaller's `.spec` file controls what kind of output gets produced. Without a `BUNDLE()` call, PyInstaller on macOS would produce a bare Unix executable, not a real `.app` — something a typical Mac user has no idea how to launch. Added a `sys.platform == 'darwin'` conditional block so the Windows build path is completely untouched.

3. **Follow-up fix, same session: onefile → onedir for the darwin build only.** After the first darwin build attempt, PyInstaller's own build log emitted a warning that onefile mode is known to clash with macOS security expectations (Gatekeeper/notarization assume a normal directory-structured `.app`, not a single self-extracting binary masquerading as one). Switched the darwin build target to `onedir` mode in response to PyInstaller's own documented warning, not a guess. Windows build stays on `onefile` — unrelated platform, unrelated risk profile, no reason to change something that isn't broken there. (Turns out to be directly relevant to the separate Windows auto-update crash flagged below — same underlying onefile fragility, different trigger.)

**New file: `.github/workflows/build-macos-test.yml`.** Deliberately kept separate from the existing tag-triggered `build.yml` release pipeline:
- Trigger: `workflow_dispatch` only — manual, on-demand, never fires automatically.
- Runner: `macos-14` (Apple Silicon) — matches real modern Mac hardware, not an Intel runner.
- Builds via PyInstaller using the updated `.spec`, then zips the resulting `.app` using macOS's own `ditto` utility rather than a generic zip tool — `ditto` preserves macOS-specific bundle metadata (resource forks, extended attributes) that a plain `zip` command can silently strip, which would produce a corrupted-looking `.app` on the receiving end.
- Uploads the zip as a **GitHub Actions workflow artifact**, not attached to a GitHub Release — this is explicitly a test build, not a versioned public release, and shouldn't appear alongside real tagged releases.

**Verification performed before sending anything to the tester:**
- Downloaded the workflow artifact and confirmed the `.app` bundle's internal structure — a `Frameworks` folder was present inside the bundle, which is the concrete, checkable signal that `onedir` mode actually took effect (onefile mode wouldn't produce this folder structure).
- Size sanity-checked: ~27MB, consistent with a Python/PyQt app bundle, not suspiciously bloated or truncated.
- PyInstaller's own `warn-pingguard.txt` build-warning log was read directly rather than assumed clean — contained only expected, harmless missing-module warnings (the normal noise for optional/platform-specific imports PyInstaller can't resolve on the build machine), nothing indicating a real packaging problem.
- Searched for remaining `winreg` references across the codebase to confirm the `game_detector.py` fix was the only site that mattered — found one additional reference inside `app.py`, confirmed it was already safely platform-gated (not a second unguarded import that would have crashed independently of the `game_detector.py` fix).

**Delivered to the tester** along with a plain-English "how to open this + what to actually click on and test" guide, written for a non-technical recipient (same target-audience framing PingGuard uses everywhere else).

**Explicitly not yet true — don't overstate this milestone:** this confirms the build *packages* correctly. It does **not** yet confirm the app *runs* correctly end-to-end on real macOS hardware — no tester usage report has come back yet. Treat as "packaging verified, runtime unverified" until that report arrives.

---

## Security Incident — Resolved (Session 20)

**Factual summary only — no speculation, no unresolved threads left dangling.** Nathan's dev PC had a genuine malware infection during this period. It was unrelated to PingGuard or StartGuard — logged here for completeness and because it triggered a real supply-chain audit of both projects, not because the malware itself has any further relevance to this codebase.

**Audit performed, both GitHub repos:** commit history, all workflow files (`.github/workflows/*`), `requirements.txt`, `updater.py`, and `reporter.py` were reviewed directly for any sign of tampering, injected dependencies, or modified build/release logic. **Found: no tampering in either repo.**

**Fresh VirusTotal scans run against both apps' actual current release installers** (not source, the real shipped binaries): both came back clean apart from well-documented, low-signal false positives already understood from prior sessions — `Wacatac.B!ml` (a single-vendor Microsoft Defender heuristic) on PingGuard's installer, and a similarly generic low-signal flag on StartGuard's. This is the same known PyInstaller-produced-executable false-positive pattern already documented elsewhere in this project's history, not a new or different signature.

**Outcome: no user-facing action was required.** No advisory, no forced update, no installer pull — the installers themselves were never compromised.

**Machine-level remediation:** the local dev machine was reinstalled clean. The project folder (this repo, working tree, everything) survived intact because it lives on a separate physical drive from the OS install. Toolchain — git, Claude Code — was reinstalled and reconfigured on the fresh OS install before resuming work this session.

---

## Process Detection — Architecture (Hardened Session 16, Confirmed Live Session 17)

**Confirmed via direct review of `app.py`, `main_window.py`, and `ping_engine.py`:** the `exe` field is used *only* for "is this game currently running" detection inside `PingWorker.check_running_games()`. It has zero connection to the actual ping test, which runs purely off `host`/`port`. A stale/wrong `exe` value can never break ping accuracy — it only affects the "▶ Running" badge and the check-on-launch trigger.

**The fix, generalized into a standing pattern:** `exe` / `exe_mac` / `exe_linux` can now be **either a single string or a list of accepted aliases**. Apex Legends' `exe` is now `["r5apex.exe", "r5apex_dx12.exe"]`. `ping_engine.py`'s `get_process_names_for_game()` (replacing the old singular `get_process_name_for_game()`) and a new `_as_list()` helper handle both forms transparently. Confirmed safe to rename — the old function had no callers outside `ping_engine.py`.

**Session 17 confirmation: this all works correctly end to end.** A real live Apex Legends launch correctly populated the "▶ Running" bar and produced real ping history.

---

## Region Separation System — Architecture (Built Session 15)

**The problem:** several `DEFAULT_GAMES` entries blend multiple regions into one game with a fallback endpoint list. Confirmed via `ping_engine.py`: a TCP connection that's actively *refused* still counts as a successful ping — so the first endpoint in a list almost always "succeeds," and any fallback after it is effectively dead code.

**Critical architecture fact:** `DEFAULT_GAMES` only matters once — the very first time a user launches the app. After that, `games.json` on disk is the real source of truth and `DEFAULT_GAMES` is never consulted again. Any change to `games.py` alone is silently invisible to every existing install unless paired with a migration in `settings.py`.

**Also critical, reconfirmed independently twice more this session (the Apex duplicate-name bug and the Warzone migration work):** `GameManager.update_ping()`, `remove_game()`, and `update_game()` all match games purely by `game["name"] == name`. The name string **is** the identity of a game in this data model.

**The fix, built and validated Session 15:** standalone entries per region (`"Overwatch 2 (EU)"` / `"Overwatch 2 (NA)"`), a `migrate_game_regions()` function in `settings.py` that runs the migration automatically, and a rebuilt setup wizard using real, fixed AWS regional endpoints (`ec2.<region>.amazonaws.com`) instead of Battle.net's CDN-fronted domains, after the first attempt returned a physically impossible 7ms for a distant region from Cape Town.

### Explicitly NOT done yet (don't assume otherwise):
- **Call of Duty: Warzone's dead fallback is fixed (Session 17), but it is NOT a regional split** — see the dedicated section above for exactly why that pattern isn't available for this game right now.
- **The other ~16 games in `DEFAULT_GAMES`** haven't been audited for the same blended-region issue. The `trace_connections.py` + WHOIS-verification method used for Warzone is now a proven, reusable process for this audit going forward.
- **A real per-game region management screen** doesn't exist yet.

---

## Icon Build Process — PingGuard-Specific Notes
Same base technique as StartGuard (gradual shrink + sharpen for small sizes, manual ICO builder via `struct`). PingGuard-specific refinement: thin detail (the crosshair) vanishing at 16px fixed via enlarging the inner target ~1.3x with a soft radial blend mask for the smallest sizes only. Full detail preserved from Session 14.

## Icon Wiring — Confirmed Working (Session 14)
Full chain verified via the actual built `.exe`: title bar, taskbar, tray, and Windows notifications all correct. AppUserModelID set in `main.py` as a defensive layer.

---

## Header Logo — Real Shield/Target Icon Replaces Emoji (Session 24)

**The problem:** `main_window.py`'s header title was `QLabel("🎮 PingGuard")` — a generic controller emoji, not any of PingGuard's own branding, despite the app already having real shield/target art (`assets/icon.ico`) used for the taskbar icon.

**The fix:** extracted a new transparent asset from the existing `assets/icon.ico` (not the separate promotional banner graphic supplied for reference) so the header matches the taskbar exactly. First pass kept the icon's solid interior fill and came out looking like an opaque box in light theme — the interior fill turned out to be baked into the source art itself, not a transparency bug. Rebuilt as pure line art instead: kept only pixels matching the outline/crosshair's blue (which is almost exactly the app's own accent color, `#4c4cff`), discarded everything else including the interior, so it's genuinely theme-adaptive with no separate light/dark variant needed. Stroke width thickened (dilated) and displayed size increased to 42px tall after visual review in both themes.

**New file:** `assets/icon_header.png`. `main_window.py`'s header now shows this pixmap (via `resource_path()`, same pattern as `icon.ico`) followed by a plain `"PingGuard"` text label (previously the emoji+text were one label) — the text itself is untouched, still theme-driven via `t['text_bright']`. `pingguard.spec`'s `datas` list updated to bundle the new asset — it was listing individual files, not the whole `assets/` folder, so a new file dropped in wouldn't have shipped in the installer without this.

**Confirmed working, both themes, after two rounds of visual feedback** (interior-fill box in light mode → line-art rebuild; too small/thin → bigger + thicker stroke).

---

## License Viewer + Version Display (Session 23)

**Goal:** two small, independent Settings-dialog features, both deferred from Session 22 — an in-app license viewer and a version/update-available indicator.

**1. In-app license viewer.**
- `LICENSE.txt` created at the project root — a new file for PingGuard, did not exist in this repo before this session. UTF-8 encoded, content matches the shared JackalNode Master Licence text used across JackalNode's free apps, with the title changed to "JackalNode Licence" (not "StartGuard Licence" or "PingGuard Licence"), per the standing one-canonical-text-across-all-free-apps convention. Verified at the byte level that the £ symbol in Section 3 encoded correctly (`c2 a3`, valid UTF-8).
- `settings_dialog.py`: added `_license_path()` and `_load_license_text()` helpers, following the frozen/source detection pattern already used by `resource_path()` elsewhere in the codebase. New `LicenseDialog(QDialog)` class — read-only `QTextEdit`, 440×360, themed. New "View License" button wired into `_build_ui`.
- `pingguard.spec`: added `('LICENSE.txt', '.')` to `datas`.

**2. Version display + update-available indicator.**
- `settings_dialog.py`: added a `version_label` under the Settings title, showing `"PingGuard v{version}"` (read via `QApplication.instance().applicationVersion()`). A passive `UpdateCheckWorker` (instantiated on `SettingsDialog` init, using the same `"PingGuard"` / `"pingguard"` literals as `app.py`'s real `check_for_updates()` call site) updates the label to `"Update available (vX.X.X)"` if a newer GitHub release exists. No popup — a quiet indicator only, separate from the existing startup `check_for_updates()` flow, which still shows the full `UpdateDialog`.

**Verification, both features:** dev run (both features, both themes); a forced test using a hardcoded older version string temporarily passed to `UpdateCheckWorker` to confirm the update-available label renders correctly, reverted before commit; a full PyInstaller build with `Get-ChildItem` confirming `LICENSE.txt` actually landed in the onedir output; the built `PingGuard.exe` re-tested against the same checklist.

**VirusTotal note:** v2.2.3's installer showed the same known Wacatac.B!ml + Arctic Wolf heuristic pair already documented for prior releases (2/70 vendors). Confirmed via identical file hash against an earlier clean scan of the same binary that this is VirusTotal's heuristic engines re-evaluating over time, not a build-specific issue — not actioned, consistent with established project history.

**Shipped as v2.2.3** — committed as two separate commits, version bumped in both required locations, tagged and pushed, GitHub Actions green on both Windows and macOS jobs, itch.io manually updated to current for the first time since v2.2.0.

---

## Riot Status Check — Replacing TCP Ping for Valorant/LoL (Session 25/26 — COMPLETE)

**Why this exists.** Session 19 confirmed architecturally that TCP ping can never measure real Valorant/LoL match latency — both titles' real game processes use unconnected (`sendto()`-style) UDP sockets, invisible to any OS-connection-table tool, confirmed via raw `netstat` on both titles independently. The existing endpoints (`euw1.pvp.net`/`eu.api.riotgames.com` for Valorant, `euw1.api.riotgames.com`/`eu.api.riotgames.com` for LoL) were shipped unchanged, documented as measuring login/API latency only. Session 25 is the first real attempt at solving that gap properly, rather than living with the caveat: instead of trying to measure match latency at all, it replaces the ping display for these two titles with a real Riot service-status check.

**What it looks like, confirmed via live screenshots:** for Valorant and League of Legends specifically, the normal ms readout + sparkline is replaced with colored status text — green **"Online"** or amber/orange **"Game Server Unavailable"** — with the row's status dot colored to match. Every other game (CS2, Apex, Overwatch, etc.) is unaffected and still shows ms + sparkline as before.

**Resolved Session 26.** A Claude Code session with real read access to `E:\Projects\PingGuard v3\PingGuard` (not another upload) read the literal current `app.py`, `logger.py`, `main_window.py`, `games.py`, `settings.py`, `ping_engine.py`, and `settings_dialog.py` directly, confirming both bugs' exact mechanism before touching anything. `app.py` and `logger.py` turned out correct and untouched by the original Session 25 work — both already handled `StatusResult` correctly via `isinstance()` checks. The actual bugs lived entirely in `main_window.py`, `games.py`, `settings.py`, and `ping_engine.py`.

**Two real bugs, both root-caused from literal source and fixed in Session 26:**

1. **Row click-to-expand was broken for Valorant/LoL, worked fine everywhere else — FIXED.** Root cause, confirmed in `main_window.py`'s `GameRow.mousePressEvent()`: an explicit `if self.is_status_game: ... return` branch skipped `_toggle_expand()` entirely for status rows — a deliberate choice made during the original Session 25 work, not a side effect. `PingHistoryChart` already renders "No data yet" for empty history, so there was no functional reason for the special case. Fix: removed the branch. Status rows now toggle open/closed like every other row.
2. **The status check ignored the existing "Your Region" setting — FIXED.** Root cause, confirmed in `ping_engine.py`: `check_riot_status(game, timeout=5.0)` built its URL from a single hardcoded `game["status_shard"]` ("eu" for Valorant, "euw1" for League, both in `games.py`), and `PingWorker._ping_one()` called it with no region argument — `settings.get("user_region")` was never read in this path. Fix: replaced `status_shard` with a `status_shards` dict mapping every selectable region to a real Riot shard, live-verified one by one by fetching `https://{platform}.secure.dyn.riotcdn.net/channels/public/x/status/{shard}.json` directly and confirming distinct real per-shard data came back. `check_riot_status()` now takes `user_region`; `PingWorker._ping_one()` passes `settings.get("user_region", "EU")` through.

   **Region list expanded 5→8 — stress-tested first, not assumed.** Added **Korea** and **Brazil**: confirmed live that Riot runs them as genuinely separate shards from the broader Asia/SA buckets for Valorant (`ap`≠`kr`, `latam`≠`br`) and for League's SA bucket (`la1`≠`br1`). League has no general Asia-Pacific shard, so League's Asia and Korea intentionally resolve to the identical `kr1` — not a bug, just Riot's real ceiling for that title. Added **Africa**: `setup_wizard.py`'s first-run picker already offered "Africa" (its own AWS latency test) but nothing downstream recognized it as a value — a latent bug found while reading source for this fix. Africa now maps to each game's EU shard.

   Full maps: Valorant `{"EU":"eu","NA":"na","Asia":"ap","Korea":"kr","SA":"latam","Brazil":"br","OCE":"ap","Africa":"eu"}`; League `{"EU":"euw1","NA":"na1","Asia":"kr1","Korea":"kr1","SA":"la1","Brazil":"br1","OCE":"oc1","Africa":"euw1"}`.

   **Verified end-to-end against real, independently-confirmed live incidents — not a clean-everywhere test that could pass by coincidence.** At verification time Valorant's `eu` shard genuinely had two active incidents (Dubai/Bahrain "Game Server Unavailable") and League's `br1` genuinely had one ("Gifts") — both reconfirmed live immediately before testing. Switching Region to EU/Africa correctly surfaced the Valorant notice; switching to Brazil correctly surfaced the League notice while Valorant read Online; switching to NA/Korea showed both Online (genuinely clean). Each real incident surfaced only when its actual region was selected.

**Session 26 outcome:** all items above are done. The click-to-expand decision resolved in favor of consistency — status rows always toggle open, showing "No data yet" same as any other empty-history row. `migrate_game_status_source()` in `settings.py` updated to patch existing installs from the old single `status_shard` field (or no Riot-status fields at all) onto the new `status_shards` map on next launch; tested for idempotency — converts on first run, reports no further change on a second run against already-migrated data.

---

## Ping Jitter — DNS Cache-Miss Root Cause & Fix (Session 27)

**Why this exists.** Session 24 surfaced an unexplained finding while verifying the FFXIV endpoint fix: an isolated, sequential test of `neolobby06.ffxiv.com:54994` was rock-stable (158-166ms), but the same endpoint swung 159-818ms inside a real all-games `ping_all()` cycle. The working theory going in was `ping_all()`'s unthrottled one-thread-per-game design — no cap, no stagger — contending for network/OS resources. Flagged as "not confirmed root-caused" and left as a Still To Do item.

**Root-caused via two independent live test scripts, not assumed.** `jitter_test.py` (kept as a standalone diagnostic, not shipped) ran four interleaved, paced conditions against the same FFXIV endpoint every round for 30 minutes: isolated sequential, an exact `ping_all()` replica (unthrottled parallel), a capped thread pool, and staggered thread starts. Result: the unthrottled-parallel condition — the exact current app behavior — was consistently the *cleanest* of all four (1 spike in 60 rounds), while the isolated-sequential condition carried nearly all the jitter (14 spikes in 60 rounds) — the opposite of what the concurrency theory predicted. Isolated pings also clustered their spikes on an almost exact ~60-second period, and no other condition ever spiked in the same round as isolated — whatever slowed it down cleared again within about a second.

**Follow-up isolated the real mechanism: OS-level DNS cache expiry, not threading.** `dns_isolation_test.py` (also kept as a standalone diagnostic) timed `socket.getaddrinfo()` alone, a real `tcp_ping()` call via hostname, and a `tcp_ping()` call via the already-resolved numeric IP, interleaved every round for 25 minutes. DNS-resolution time and hostname-ping time spiked together; IP-only pings (no resolution step) never spiked. Combined across both scripts, 135 test rounds, 0 showed a second call to the same host inherit the first call's spike — confirming Windows' DNS Client service caches a hostname resolution system-wide until its TTL expires, and whichever caller is first to query after expiry pays the real upstream-lookup cost (150-450ms observed), while any caller immediately after (same or different process) rides the now-warm cache.

**Fix: a discard-first warm-up ping, not an app-level IP cache.** `PingWorker._ping_one()` now performs the real check (status check or TCP ping) twice per cycle, per game — the first result is thrown away, the second is what gets recorded and displayed. This defeats the DNS-cache-miss cost directly without introducing IP staleness risk — Apex Legends and Warzone are both documented (Session 18) as having dynamic per-match datacenter assignment, so caching a resolved IP ourselves for any length of time risks pinging last match's server. Doubling the per-cycle call count (21→42) is trivial overhead at the real `auto_check_interval` cadence (120s default).

**Separately: full pause of background pinging while a monitored game is running.** Raised by the dev during this session — notifications popping up mid-match, and any latency contention from PingGuard's own background pinging however small, are both worth eliminating outright while actually playing. `_auto_tick()` in `app.py` now returns early (no countdown decrement, no auto-fired `ping_all()`, and therefore no notifications, since those only ever fire from a ping result) whenever `PingWorker.get_running_games()` reports anything running. The existing `check_on_game_launch` one-off check (5s after a game is first detected, in `_on_game_detected()`) is untouched and still fires — that's the pre-match reading this feature exists to give. Resumes automatically once the existing 10s-interval `check_running_games()` reports nothing running. Dev explicitly confirmed "Full pause" over two lighter alternatives when asked. Scope note: this only ever engages for games already tracked in `games.json`, since `get_running_games()` is a pure process-name check against the same tracked list `check_on_game_launch` already uses — an untracked game never pauses anything, not a new limitation.

**Live-verified, not just tested standalone.** Both fixes were run in the real app: League of Legends (Riot-status code path) and CS2 (plain `tcp_ping` code path) both confirmed the pause engaging correctly — countdown freezes on game detection (including from CS2's menu screen, before a match even starts, since detection is process-based), no notifications fire, and it resumes within ~10s of the game closing, cross-checked via internally-consistent countdown/timestamp math across paired screenshots each time. A ~2-hour real background run was used to check the DNS-jitter fix's effect on FFXIV's live chart: min 161 / avg 200 / max 510ms across a 60-sample (~1hr) window — a large drop in frequency from the original 159-818ms-swinging description, but **not a full elimination**: one ~510ms spike still got through. Likely genuine one-off network/server jitter rather than a hole in the fix (the warm-up ping populates the OS DNS cache regardless of whether its own connection succeeds, so a timed-out warm-up shouldn't leave the cache cold for the recorded call) — but this is not confirmed, only inferred from the fix's mechanism. Not investigated further; worth a dedicated look only if this class of spike recurs at a real rate in ongoing use, not from one occurrence.

**Outcome:** both fixes applied to `ping_engine.py` and `app.py`, verified via `py_compile` and diff before applying, committed as a single commit (`0e86f4f`) alongside the two new diagnostic scripts, and pushed to `main`. Not yet tagged or built into a release — see Session Log.

---

## File Inventory

| File | Status | Notes |
|------|--------|-------|
| `main.py` | ✅ Stable | Version `2.2.3`. AppUserModelID set before `QApplication` is created. |
| `app.py` | ✅ Updated (Session 26 & 27) | Read directly from source: `_on_ping_result()`'s `isinstance(result, StatusResult)` branch correctly skips ms/threshold logic and only alerts on a real "issue" — unaffected by the region fix, untouched Session 26. **Session 27:** `_auto_tick()` now returns early (no countdown, no auto-fired `ping_all()`, no notifications) whenever `PingWorker.get_running_games()` reports anything running — full pause while a monitored game is playing. Live-verified on both the Riot-status and plain `tcp_ping` code paths. |
| `settings.py` | ✅ Updated (Session 17, 18, 24 & 26) | `add_game()` duplicate-name guard (Session 17). `migrate_game_endpoints()` Warzone and Apex Legends entries (Session 17/18); Path of Exile entry added, plus the function's apply loop extended to optionally write an `exe` field (Session 18). **Session 24:** `add_game()` re-enables disabled matches instead of rejecting them; FFXIV entry added to `migrate_game_endpoints()`. **Session 26:** `STATUS_SOURCE_MIGRATIONS` and `migrate_game_status_source()` rebuilt around the new 8-key `status_shards` map (root cause of the Session 25 region bug) — strips any leftover `status_shard` field and writes the full map on existing installs; confirmed idempotent. |
| `main_window.py` | ✅ Fixed (Session 26) | Session 24 changes stand (header logo rebuild, `_on_add_game()` duplicate-name warning). **Session 26:** `GameRow.mousePressEvent()`'s `is_status_game` early-return removed. `GameRow.is_status_game` and `MainWindow._populate_games()` both switched from the retired `status_shard` field to `status_platform`. |
| `settings_dialog.py` | Updated (Session 23 & 26) | New `LicenseDialog` class, `_license_path()`/`_load_license_text()` helpers. "View License" button wired into `_build_ui`. New `version_label` plus a passive `UpdateCheckWorker` for a quiet update-available indicator. **Session 26:** `user_region` combo expanded from 5 to 8 options (EU/NA/Asia/Korea/SA/Brazil/OCE/Africa) — see Riot Status Check section above. |
| `games.py` | ✅ Updated (Session 16, 17, 18, 24 & 26) | Apex Legends `exe` alias list (Session 16). Warzone endpoint fix (Session 17). Apex Legends `endpoints`/`region_note` fixed with a WHOIS- and live-trace-confirmed AWS address (Session 18). Path of Exile `endpoints` replaced with a WHOIS- and live-trace-confirmed Google Cloud address; `exe` updated to alias list (Session 18). **Session 24:** FFXIV `endpoints` replaced with the live-verified `neolobby06.ffxiv.com:54994`. **Session 26:** Valorant's and League's single `status_shard` replaced with an 8-key `status_shards` map (EU/NA/Asia/Korea/SA/Brazil/OCE/Africa), every code live-verified against Riot's real status endpoints. |
| `add_game_dialog.py` | ✅ Updated (Session 16), confirmed working Session 17 | Server Address field clarity fix: relabeled, tooltip added, explanatory hint added, dialog height bumped 520→555. |
| `game_detector.py` | ✅ Updated (Session 20) | Steam/Epic/Riot/Battle.net detection. `winreg` import guard corrected for macOS test build — platform check now placed before any unguarded reference, not just wrapping the import line. |
| `reporter.py` | ✅ Updated (Session 22) | send_game_request() + send_report() + new send_update_report() — mirrors send_game_request()'s pattern, no game dependency, powers the "Report an Issue" button in the update-flow dialogs. |
| `updater.py` | ✅ Updated (Session 22) | Fully platform-aware: _find_installer_url() branches on sys.platform, _start_download() derives extension from platform, _on_download_done() is a clean win32/darwin two-way branch. check_failed signal now carries a reason ("error"/"no_asset"). |
| `setup_wizard.py` | ✅ Reviewed Session 17, unchanged | Confirmed it does not call `GameManager.add_game()`. |
| `ping_engine.py` | ✅ Updated (Session 16, 26 & 27), confirmed working live Session 17 | `get_process_names_for_game()` + `_as_list()` helper. `tcp_ping()` reused directly (unmodified) to verify Warzone's Demonware endpoint at 248ms. **Session 26:** `check_riot_status()` now takes `user_region` and resolves the shard from the game's `status_shards` map instead of a hardcoded field; `PingWorker._ping_one()` passes `settings.get("user_region", "EU")` through — fixes the confirmed Session 25 region bug. **Session 27:** `_ping_one()` now fires the real check twice per cycle per game, discarding the first result — a warm-up ping that defeats the DNS-cache-TTL-expiry jitter root-caused this session. See dedicated section above. |
| `trace_connections.py` | 🆕 New (Session 17) | Standalone diagnostic script, not part of the shipped app. Uses `psutil` to list a named running process's real active connections. Built to verify Warzone's real server; reusable for auditing any other game going forward, and serves as a working proof-of-concept for the previously-flagged "psutil-based Server Address auto-fill" idea. |
| `jitter_test.py` | 🆕 New (Session 27) | Standalone diagnostic script, not part of the shipped app. Imports the real `tcp_ping`/`check_riot_status`/`ping_game`/`DEFAULT_GAMES` and runs four interleaved, paced conditions (isolated sequential, exact `ping_all()` replica, capped thread pool, staggered threads) against the FFXIV endpoint every round for 30 minutes — disconfirmed the unthrottled-parallelism jitter theory. |
| `dns_isolation_test.py` | 🆕 New (Session 27) | Standalone diagnostic script, not part of the shipped app. Follow-up to `jitter_test.py` — times `getaddrinfo()` alone, a real `tcp_ping()` via hostname, and `tcp_ping()` via the already-resolved IP, interleaved every round for 25 minutes. Isolated the real jitter mechanism to OS DNS-cache-TTL expiry. |
| `logger.py` | ✅ Confirmed (Session 26) | Discovered Session 15, not touched through Session 24. Read directly from source: `log()`'s `isinstance(result, StatusResult)` branch is correct and complete as-is — no changes needed, unaffected by the region fix. |
| `theme.py` | ✅ Stable | No changes since Session 14. |
| `reporter.py` / `constants.py` / `constants_example.py` | ✅ Stable | Webhook handling unchanged. |
| `pingguard.spec` | ✅ Updated (Session 20, 21, 23 & 24) | Darwin-only `BUNDLE()` block added; darwin build target switched onefile → onedir after PyInstaller's own build-log warning. Windows onedir branch added Session 21 (see below). **Session 23:** `('LICENSE.txt', '.')` added to `datas` so the license text ships inside the onedir output on both platforms. **Session 24:** `('assets/icon_header.png', 'assets')` added — the `datas` list names individual files, not the whole `assets/` folder, so the new header logo needed its own entry to actually ship in future installer builds. |
| `.github/workflows/build-macos-test.yml` | 🆕 New (Session 20) | Manual `workflow_dispatch` only, `macos-14` runner. Builds via PyInstaller, zips the `.app` with `ditto` (preserves macOS bundle metadata a plain zip would strip), uploads as a workflow artifact — not attached to a GitHub Release, deliberately separate from the tag-triggered `build.yml` pipeline. |
| `PingGuard.iss` / `requirements.txt` / `.github/workflows/build.yml` / `.gitignore` | ✅ Stable | No changes this session. |
**Session 21 file updates (Windows onedir migration):**
- `pingguard.spec` — new `elif sys.platform == 'win32':` branch added, mirroring the existing darwin `COLLECT()` pattern (no `BUNDLE()`, that's macOS-only). `exclude_binaries` and the `a.binaries`/`a.datas` exclusion widened from darwin-only to `('darwin', 'win32')`. Darwin block itself untouched.
- `PingGuard.iss` — `[Files]` section's Windows source changed from a single named file to a recursive wildcard (`dist\PingGuard\*`, `recursesubdirs createallsubdirs`) to package the full onedir folder output. `#define MyAppVersion` bumped 2.2.0 → 2.2.1.
- `main.py` — version bumped to 2.2.1 (`app.setApplicationVersion("2.2.1")`).

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
- **Standing pattern (Session 16): `exe` / `exe_mac` / `exe_linux` can be a single string or a list of accepted aliases.**
- **New standing pattern (Session 17): a game's name is its sole identity everywhere in this data model, and that is now actually enforced.** `GameManager.add_game()` refuses to add a game whose name already exists, returning `False` instead of silently appending.
- **New standing pattern (Session 17): any entry added to `migrate_game_endpoints()`'s `fixes` dict must carry its own `is_stale` check and its own `region_note` — never a shared/broad condition across multiple games.** A correct new address for one game can coincidentally collide with another game's old-bad-address prefix check (proven this session: Warzone's real `185.34.106.103` vs CS2/Dota2's old-bad `185.x` check).
- **New architecture fact (Session 17): Call of Duty's actual game servers run on Demonware (Activision's own networking subsidiary), confirmed via RIPE WHOIS — not Battle.net.** Battle.net is only the PC login/launcher layer for Activision titles, unlike genuine Blizzard titles where it is the real backend. Demonware does not appear to expose fixed, named regional addresses the way Battle.net does — matchmaking dynamically assigns datacenters, observed to vary. This is why a full Overwatch-2-style regional split isn't currently available for Warzone.
- **Process lesson, reinforced three times this session (Apex data, the Grep/edit-status mismatch, the `migrate_game_endpoints()` description): when an agent's claim about file or code content doesn't match — or hasn't yet been checked against — the literal content, ask for the literal content before proceeding.** This is now a hard standing rule for this project, not a one-off catch. **Session 25 reinforced this again from the doc-writing side:** a compacted chat summary describing a diff in prose ("app.py's import and `_on_ping_result` are letter-for-letter what I asked for") is not the same as having seen the diff — treat it as unverified, same as any other second-hand description, until the literal current source is read.
- **New architecture fact (Session 18), generalizing the Session 17 Warzone finding: dynamic per-match datacenter assignment is not Call-of-Duty-specific.** Confirmed directly via live in-game evidence on Apex Legends — PingGuard's verified, WHOIS-confirmed AWS endpoint (`us-east-1`) didn't match the in-game datacenter readout (`sa-east-1`) on a later match. Any title using cloud-hosted, matchmaking-assigned dedicated servers should be assumed to share this limitation by default during future audits, rather than treated as a special case to check for individually.
- **New standing pattern (Session 18): `migrate_game_endpoints()`'s fix dict format extended to support an optional `'exe'` key, applied via a guarded line in the apply loop (`if 'exe' in fix: game['exe'] = fix['exe']`).** Confirmed this cannot affect any existing fix entry without that key. This is the first mechanism in the codebase for migrating a game's `exe` value on existing installs — previously only `endpoints` and `region_note` could be migrated.
- **Open question flagged (Session 18): Apex Legends's exe alias generalization (Session 16/17) was confirmed working live via real testing, but no corresponding `migrate_game_endpoints()` exe entry was ever added for it at the time — the capability didn't exist yet.** Worth confirming next session whether Apex's existing `games.json` entry already has the correct alias list (possibly written incidentally during the Session 17 duplicate-name manual merge) or whether it's relying on something else. Not urgent, but worth closing the loop now that the mechanism exists to actually fix it if needed.
- **New fact (Session 18): the "missing games" symptom reported by the dev was not a bug.** `_populate_games()` in `main_window.py` filters purely on a per-game `enabled` boolean (defaulting to `True` if missing) — confirmed via literal source, no category/search filtering exists. Only 6 of the 21 `DEFAULT_GAMES` entries were actually enabled in the dev's real `games.json` (Apex, Overwatch 2 EU/NA, World of Warcraft, League of Legends, Rainbow Six Siege). All 21 were set to enabled during this session to support ongoing endpoint-audit testing, and the dev intends to leave them enabled going forward — meaning PingGuard's monitoring loop is now actively pinging all 21 default games' endpoints on every cycle, not just 6.
- **New architecture fact (Session 19): three distinct classes of audit-blocking issue are now confirmed for this project** — (1) CDN-shadowing, a real correct address exists and just needs finding (Warzone/Apex/PoE); (2) dynamic per-match datacenter assignment, a real address exists but changes session to session (Warzone/Apex); (3) unconnected/`sendto()`-style UDP sockets, the OS itself never records a remote peer, making the address invisible to any connection-table tool regardless of permissions (Valorant, confirmed via raw `netstat`, independent of `psutil`/Vanguard). Check for class (3) early via `netstat`'s UDP remote-address column before investing in a full WHOIS pass.
- **Refinement to the Session 19 three-class framework: Valve's Steam Datagram Relay (SDR) is now a confirmed, specific instance of class 3 (unconnected UDP) for CS2, and almost certainly for Dota 2 by inference.** Unlike Valorant's case, SDR's IP-hiding isn't incidental netcode behavior — it's Valve's explicit, documented anti-DDoS design. Worth assuming by default for any Steamworks-API title going forward, rather than treated as a one-off. CS2 and Dota 2's existing `region_note` of "Steam servers" turned out to already be an honest label rather than something needing correction, unlike Warzone's old fallback.
- **Refinement to the Session 19 architecture findings: Riot's unconnected-UDP pattern (first confirmed on Valorant) now confirmed on League of Legends too** — a much older title on a completely different engine, run by the same company. Worth treating as a default assumption for any further Riot title, the same way Steam Datagram Relay is now assumed by default for Steamworks titles. **Session 25: this is the finding that directly motivated the Riot status-check replacement** — see dedicated section above.

---

## Planned — Report-System Trace Collection (Fast-follow after v2.2.0)

Opt-in, disclosed feature: prompt players (scoped only to games still flagged unverified, not all 21) to send a short live-connection trace via the existing `reporter.py` → Discord webhook pipeline, reusing the proven `trace_connections.py` logic. Multi-sample over roughly 30–60 seconds rather than a single snapshot, since every successful trace this project (PoE, Warzone, Apex) needed multiple runs to separate the consistent real address from CDN/account-layer noise.

**Precondition, not yet done:** check each target game's hardcoded `exe` value isn't stale before relying on this — a stale exe means the trace silently finds nothing, which must not be mistaken for "no real server traffic" (same shape of bug as Apex's old `r5apex.exe` mismatch).

Does not touch `games.py`, `GameManager`, or the core data model — additive only. Ships as its own patch after v2.2.0's tag; doesn't block it.

---

## Planned — Internal JackalNode Filtering Tool (Future, not public release)

A personal-use-only tool (distinct from the public JackalNode app pipeline — no "plain English" constraint, no donation-only model) that ingests raw player connection-trace reports and automates the WHOIS/CDN-pattern judgment currently done by hand each audit session. Sequenced after the report-system feature above ships and has real report data to work against; ranked ahead of starting any new unstarted public-pipeline app (SlowDown?, DriverWatch, etc.).

**Design requirement:** must be agent-operable from the start. The dev is building a personal AI assistant intended to eventually run/view this tool in his stead — write actions always require his explicit approval. Output should be structured data, not prose, so the assistant can act on results reliably.

---

## Release Sequence — Roadmap

### v2.0.5 / v2.0.6 — Patch: Bug Fixes & Infrastructure Parity ✅ SHIPPED
### v2.1.0 — Icon Completion + Light/Dark Theme + Cleanup ✅ SHIPPED

### v2.2.0 — Minor: Per-Game Management ✅ CHECKLIST COMPLETE, PENDING TAG
*Moderate risk — touches the core data model and monitoring loop.*
- ✅ Add Game auto-detection (Steam/Epic/Riot/Battle.net)
- ✅ Region-separation architecture, migration, and wizard rebuild (Overwatch 2 as worked example)
- ✅ Add Game host-field clarity fix (Session 16)
- ✅ Apex Legends exe mismatch fixed + generalized into exe-alias architecture (Session 16/17)
- ✅ Duplicate-game-name data corruption bug found, root-caused, and fixed (Session 17)
- ✅ Call of Duty: Warzone's dead/fake fallback endpoint replaced with a verified real Demonware address, with a corresponding `migrate_game_endpoints()` fix for existing installs (Session 17) — **note: this is a verified endpoint correction, not a full regional split.** EU/NA separation for Warzone remains unavailable, not just undone, since Demonware doesn't expose fixed regional addresses the way Battle.net does.
- ✅ Apex Legends endpoint audited and fixed (Session 18) — CDN-shadowing bug fixed, endpoint replaced with WHOIS- and live-trace-confirmed AWS address. **Known accepted limitation, not fully resolved:** confirmed live that Apex's matchmaking assigns different datacenters per match, so the fixed endpoint is correct only when a match happens to land in the same region it was captured in. Same shape as Warzone's unresolved `eu.battle.net` question — real per-match server detection is v3 scope.
- ✅ Path of Exile endpoint audited and fixed (Session 18) — same CDN-shadowing pattern as Apex, fixed with a WHOIS-confirmed Google Cloud endpoint. Verified against two independent ground-truth numbers (in-game gateway screenshot showing 22ms, live in-app testing showing 27ms vs a 32ms in-game lobby reading) — tightest confirmation margin of any fix this session. Stale `exe` value (`PathOfExile.exe` vs the real `PathOfExileSteam.exe`) also fixed, which required extending `migrate_game_endpoints()` to support exe-field migrations for the first time.
- 🟡 World of Warcraft endpoint audited (Session 19) — DNS-resolved to Google Cloud, but ownership data alone can't confirm or rule out a real Blizzard backend. Live verification blocked by lack of an active subscription. Shipping as-is, unverified, relying on player error reports going forward.
- 🟡 Valorant endpoint audited (Session 19) — architecturally blocked, not fixable via this method: real-time gameplay data confirmed (via Riot's own port docs + raw `netstat`) to run over unconnected UDP sockets, invisible to any OS-connection-table-based tool. Shipping existing TCP-only endpoints unchanged, documented as login/API latency only. **Superseded by Session 25's Riot status-check work — see dedicated section above; not yet finished.**
- 🟡 CS2 endpoint audited (Session 19) — architecturally blocked, more specific root cause than Valorant: confirmed via live `netstat` trace that CS2 routes match traffic through Valve's Steam Datagram Relay (SDR), which deliberately hides server IPs from clients as an anti-DDoS measure. No real server IP is ever visible to any client-side tool, by design. Shipping existing endpoints unchanged — already honestly labeled "Steam servers," nothing to fix.
- 🟡 Dota 2 endpoint status documented (Session 19) — inferred, not directly traced (dev doesn't own the game). Same Valve/Steamworks SDR architecture as CS2, confirmed via Valve's own documentation that Dota 2 was SDR's original rollout testbed. Shipping existing endpoints unchanged on inferred grounds; flagged as the one audit this session not backed by a direct trace.
- 🟡 League of Legends endpoint audited (Session 19) — architecturally blocked, same wall as Valorant: confirmed via live `netstat` trace during an active ARAM match that the real game process (`League of Legends.exe`) has zero external TCP and only one unconnected UDP socket. The separate `LeagueClient.exe` process handles all visible CDN/chat traffic. Shipping existing endpoints unchanged, documented as account/API latency only. Confirms Riot's UDP architecture as a company-wide pattern, not a Valorant one-off. 11 default games remain unaudited beyond Warzone/Apex/PoE/WoW/Valorant/CS2/Dota 2/LoL. **Superseded by Session 25's Riot status-check work — see dedicated section above; not yet finished.**
> **Scope decision (Session 19 follow-up):** the four remaining items below were reviewed and explicitly moved out of v2.2.0 rather than left open-ended — region management screen, per-game ping thresholds, and a real "edit existing game" UI all move to v2.3.0 as net-new features rather than fixes to something broken. The psutil-based Server Address auto-fill investigation is folded into the report-system trace collection feature's scope instead of being built separately, since both need the same underlying connection-filtering logic. v2.2.0's actual shipped scope: Add Game auto-detection, region-separation data architecture, the duplicate-game-name fix, and the full endpoint + exe audit across all 21 default games.

> COMING SOON: Stop pinging Frankfurt when you're playing on Joburg servers.

### v2.2.3 — Patch: In-App License Viewer + Settings Version Display ✅ SHIPPED (GitHub + itch.io)
In-app license viewer (LicenseDialog, "View License" button, LICENSE.txt bundled via pingguard.spec) and a passive version/update-available indicator in Settings. Verified end-to-end via dev run, a forced update-state test, and a full built installer, across both themes. itch.io manually updated to current for the first time since v2.2.0.

### v2.2.4 — Patch: Ping Jitter Fix + Pause While Playing (bundles Sessions 24-27) — CHECKLIST COMPLETE, PENDING TAG
Bundles four sessions of committed-but-unshipped work, none individually version-bumped at the time: **Session 24** — `add_game()` re-enable-on-disabled fix, header logo replaced with real shield/target line-art, FFXIV endpoint replaced with the live-verified `neolobby06.ffxiv.com:54994`. **Session 25/26** — Valorant/LoL's ping display replaced with a real Riot service-status check (TCP ping architecturally can't measure either title's match latency), plus two follow-up bugs fixed (click-to-expand, region shard selection) and the region list expanded 5→8. **Session 27** — ping jitter root-caused (OS DNS-cache-TTL expiry, not the originally-suspected thread concurrency) and fixed via a discard-first warm-up ping; full pause of background pinging/notifications added while any monitored game is running. Full detail in each session's dedicated section above. `main.py` and `PingGuard.iss` version strings bumped to 2.2.4. Local build/install verification and tag/release still pending as of this entry.

### v2.3.0 — Minor (tentative): Game Search
*Only proceeds if a workable data source for game server info is confirmed.*

### v3.0.0 — Major: Network Diagnostics
*High risk — new engine, new permissions model, new UI surface. Dedicated session(s) only.*

---

## Still To Do / Open Questions
- **✅ FIXED (Session 26) — Riot status check for Valorant/LoL: both Session 25 bugs root-caused and fixed.** (1) Row click-to-expand now works — the deliberate early-return in `GameRow.mousePressEvent()` was removed. (2) "Your Region" now genuinely changes what's checked — `status_shard` replaced with a live-verified `status_shards` map, region list expanded to 8 (added Korea, Brazil, Africa). Verified end-to-end against real, independently-reconfirmed live Riot incidents. Full detail in the dedicated section above.
- **✅ FIXED (Session 21) — Windows auto-update crash, root-caused and shipped as v2.2.1.** The Session 20 crash report (`Failed to load Python DLL ... python311.dll ... module could not be found`) was investigated via a full diagnostic pull from the affected user (Jason, aka CautionHeavy — Windows Security/Defender status, Controlled Folder Access log, orphaned `_MEI` temp-extraction folders). Zero Defender detections or CFA blocks were found against PingGuard specifically — ruling out AV *blocking* as the cause. Root cause determined to be a timing/lock race during onefile's temp-folder extraction on every launch (real-time AV scanning holding a lock on `python311.dll` at the moment the bootloader tries to load it), not a targeted quarantine. Same underlying onefile fragility already confirmed on macOS (Session 20), different OS-specific trigger.
  **Fix: migrated the Windows build from onefile to onedir**, mirroring the existing darwin `COLLECT()` pattern in `pingguard.spec` (new `elif sys.platform == 'win32':` branch, `exclude_binaries` widened to cover both platforms). `PingGuard.iss`'s `[Files]` section updated from a single named-file source to a recursive wildcard (`dist\PingGuard\*`, `recursesubdirs createallsubdirs`) to package the full onedir output (`PingGuard.exe` + `_internal\`). `.github/workflows/build.yml` required **zero changes** — confirmed by full literal review; it only orchestrates PyInstaller/Inno Setup generically and was already onedir-agnostic. `updater.py` also required zero changes — confirmed it only ever hands off to the Inno Setup installer via `subprocess.Popen`, never touches individual files itself.
  **Verified before shipping:** local PyInstaller build confirmed real onedir output structure; local Inno Setup compile succeeded; fresh install tested (clean launch, correct `%APPDATA%` layout, real ping cycles against correct endpoints); upgrade path specifically tested using the real v2.2.0 onefile GitHub Release asset as a baseline (confirmed matching AppId against current `.iss`) with a deliberate marker entry (`ZZZ_UPGRADE_TEST_MARKER`) added to `games.json` before upgrading — marker survived the onedir install byte-for-byte, confirming real user data isn't lost on upgrade.
  **Shipped as v2.2.1**, tagged and built via GitHub Actions (clean run, no errors). **Confirmed fixed by Jason/CautionHeavy on his real affected machine** — the actual hardware that produced the original crash report. Held back from itch.io until his confirmation came in, per "ship to known-affected tester first" — itch.io upload still pending as of end of session.
  **Side findings from this investigation, not yet acted on:** (1) a retired pre-2.0 PingGuard uninstaller (v1.5, predates this repo's git history) was found to delete `%APPDATA%\PingGuard` outright on uninstall — since that folder is shared across all versions via Qt's org/app name resolution, any user with an old pre-2.0 install alongside a current one risks the old uninstaller wiping current save data. Not fixed, flagged for whenever legacy-install cleanup gets attention. (2) League of Legends live-match ping verification data (real in-match cross-checks done in an earlier session) is presumed lost — no longer reproducible from current chat/session history — flagged as needing re-verification whenever LoL endpoint work is revisited, not currently treated as still-confirmed.
- **Audit the other ~11 default games** for the same blended-region-fallback issue — `trace_connections.py` plus a WHOIS lookup on whatever address it surfaces is now the proven process; CoD Warzone is the worked example.
- **Audit the other ~11 default games for exe staleness** — lower priority, same "publisher renamed it" risk as Apex.
- **Whether `eu.battle.net` itself is measuring the right thing for Warzone** — flagged but not resolved this session. Since Warzone's real backend is Demonware, not Battle.net, the existing "real" half of its endpoint pair may only reflect login-service latency, not actual match-server latency. Worth a closer look before assuming Warzone's entry is now fully correct just because the fake half was replaced.
- **The GCP address on port 1119** (`35.204.122.188`) seen during the Warzone trace — port 1119 is the same port already used for WoW's real game-data endpoint elsewhere in `games.py`. Possibly a second legitimate Warzone-related server, not investigated further this session.
- **Real-time per-match server detection** — confirmed twice now (Warzone's Demonware backend, Apex's AWS multi-region matchmaking) that a single hardcoded endpoint can't represent "the server you'd actually play in" for titles with dynamic datacenter assignment. `trace_connections.py` already proves the underlying psutil-based detection works; turning it into a live, in-app feature (rather than a one-off research script) is the real fix, and now has direct evidence motivating it, not just a hunch. v3 scope.
- World of Warcraft (`eu.actual.battle.net:1119`) — DNS/ownership checked Session 19 (Google Cloud, Netherlands), inconclusive without a live trace; subscription required for that, not currently available. Shipping unverified, watching for player error reports.
- Valorant (`euw1.pvp.net:443` / `eu.api.riotgames.com:443`) — audited Session 19, confirmed architecturally blocked: real match traffic uses unconnected UDP sockets invisible to any connection-table tool. Shipping endpoints unchanged, documented as login/API latency only. Packet-capture-based detection (Wireshark) flagged as real future work, not pursued this session. **Session 25: replaced with a Riot status check instead — see dedicated section above, unfinished.**
- CS2 (`steamcommunity.com:443` / `api.steampowered.com:443`) — audited Session 19 via live `netstat` trace, confirmed architecturally blocked: real match traffic routes through Valve's Steam Datagram Relay, which deliberately hides server IPs from any client-side tool. Shipping endpoints unchanged — already honestly labeled, nothing to fix.
- Dota 2 (`steamcommunity.com:443` / `api.steampowered.com:443`) — status documented Session 19 by architectural inference only (dev doesn't own the game); same Valve SDR foundation as CS2. Shipping unchanged. Lower evidence tier than the rest of this session's audits — worth a real trace if a Dota-2-playing tester ever becomes available.
- League of Legends (`euw1.api.riotgames.com:443` / `eu.api.riotgames.com:443`) — audited Session 19 via live `netstat` trace during an active ARAM match, confirmed architecturally blocked: real game process has zero external TCP, only one unconnected UDP socket, identical to Valorant's pattern. Shipping unchanged. Misleading `region_note` values for Valorant ("EU West") and LoL ("EUW") corrected same session — see resolved note in the LoL section. **Session 25: replaced with a Riot status check instead — see dedicated section above, unfinished.**
- Confirm whether Apex Legends's `exe` alias (Session 16/17) ever actually reached the dev's `games.json` via a real migration, or whether it's relying on something else — now that an exe-migration mechanism exists (Session 18), worth a direct check.
- All 21 `DEFAULT_GAMES` entries are currently enabled in the dev's `games.json` (changed Session 18 for testing purposes, dev intends to leave as-is) — PingGuard is now actively monitoring all 21 endpoints every cycle, not just the original 6. Worth keeping in mind if performance or Discord-report noise comes up later.
- **Real per-game region management UI** — doesn't exist yet.
- **Real "edit existing game" UI** — confirmed not to exist anywhere in the app.
- **Server Address auto-fill for unlisted games** — `trace_connections.py` proves the psutil approach is viable in principle; building real filtering logic into the actual Add Game dialog is still future work.
- **macOS / Linux builds** — production pipeline builds both Windows and macOS as of Session 22. **✅ FIXED (Session 22) — macOS auto-update, root-caused and fixed end-to-end:** `build.yml` now attaches a real `PingGuard_v{version}_macOS.zip` to every tagged Release via a new `build-macos` job (sequenced via `needs: build`, no race condition), and `updater.py` was rewritten to be platform-explicit throughout, failing closed for unrecognized platforms instead of grabbing the first `.exe`. Verified via a dedicated v2.2.2 pipeline-test release — both jobs green, both assets confirmed on the Release — and confirmed end-to-end by a real Mac tester after a one-time manual bootstrap onto the new build. Future version bumps should now auto-update cleanly through the in-app flow. Linux has no test build of any kind yet — genuinely still to do.
- **Confirm workable game-server-info lookup source** before committing v2.3.0 as a real release vs. dropping it.
- **Decide scapy vs. manual raw sockets** for v3.0.0.
- **Tray icon cosmetic mismatch** — still shows a generic blue circle, not the shield art. Dev's call to leave as-is, low priority.
- **✅ FIXED (Session 24) — FFXIV's `neolobby06.ffxiv.com` lead, verified and shipped.** `frontier.ffxiv.com` confirmed to be a global (Japan-hosted) launcher status API used identically by every region, not a regional gateway. Replaced with `neolobby06.ffxiv.com:54994`, WHOIS-confirmed (Square Enix CO LTD, Frankfurt) and live-verified: ICMP baseline 161-162ms stable across 10 packets; port-scanned all five of FFXIV's officially documented game ports (54992-54994, 55006-55007) and only 54994 responds at all, matching the ICMP baseline almost exactly (158-166ms) in isolation. `games.py` and `migrate_game_endpoints()` both updated so existing installs pick up the fix automatically.
- **`api2.ea.com` — ✅ FIXED (Session 19 follow-up).** Removed from FIFA/EA FC's endpoints in games.py; corresponding is_stale entry added to migrate_game_endpoints() in settings.py for existing installs. No collision found against existing fix entries. Applied and committed.
- **Exe staleness audit (Session 19 follow-up)** — desk pass completed across all 21 default games via search-verification. No stale exe values found. Valorant, CS2, Overwatch 2 (EU/NA), Diablo IV, and Fortnite individually search-confirmed; Apex Legends and Path of Exile already live-verified in prior sessions; remaining 12 desk-checked against well-documented standard names with no discrepancies found. One soft flag, not acted on: a single support thread mentioned "Diablo Retail.exe" as a possible secondary process name for Diablo IV alongside the existing "Diablo IV.exe" — not added as an alias without further confirmation.
- **v2.2.0 — ✅ SHIPPED.** Tagged, built via GitHub Actions, installer uploaded to itch.io.
- **StartGuard's `LICENSE.txt` still shows "StartGuard Licence" as its title** — needs the same fix applied this session to PingGuard's (title corrected to the shared "JackalNode Licence"). This is StartGuard's own project's responsibility — to be handled in a dedicated StartGuard session, not here.
- **Console warning observed during Session 23's theme-toggle testing:** `QFont::setPointSize: Point size <= 0 (-1), must be greater than 0`. Non-fatal — UI rendered correctly in both Dark and Light themes, no crash. Root cause not investigated; likely somewhere in `MainWindow.apply_theme()`'s rebuild path. Predates this session's changes — neither the license viewer nor the version-display feature touch font sizing. Worth a dedicated look in a future session.
- **✅ FIXED (Session 27) — ping jitter root-caused and fixed; the Session 24 "unthrottled parallel pinging" theory was directly disconfirmed.** Two independent live A/B test scripts (135 combined rounds) found the real mechanism was an OS-level DNS-cache-TTL-expiry cost landing on whichever call is first to touch a hostname after its cached resolution expires — not thread concurrency, which was consistently the *cleanest* condition tested. Fixed with a discard-first warm-up ping in `PingWorker._ping_one()`. Full detail, including the two new standalone diagnostic scripts, in the dedicated section above.
- **New (Session 27, minor, not investigated further): one residual ~510ms spike still observed on FFXIV after the warm-up-ping fix** — 1 spike in a 60-sample (~1hr) live window, down from the original 159-818ms-swinging description but not a full elimination. Likely genuine one-off network/server jitter given the fix's mechanism (DNS resolution is cached by the warm-up regardless of whether its own connection succeeds), but unconfirmed. Revisit only if this class of spike recurs at a meaningful rate in ongoing use.

---

## Session Log
| Session | What Was Done |
|---------|--------------|
| Pre-12 | v2.0.4 shipped. Rough roadmap doc with stale URLs. Manual build process. |
| 12 | Context doc created. URLs confirmed. Feature backlog reconciled. Release sequence locked. |
| 13 | Full infrastructure parity work. GitHub Actions pipeline built. v2.0.5/v2.0.6 shipped. |
| 14 | Icon system completed end to end. Full light/dark theme system built. Dead Reporting tab removed. v2.1.0 shipped. |
| 15 | Add Game overhaul. Region separation discovered, designed, and validated via Overwatch 2. Setup wizard rebuilt twice. Newly flagged: Add Game host-field clarity gap, Apex exe mismatch, CoD Warzone region split held back, ~16 games not yet audited. |
| 16 | Add Game host-field fix. Apex Legends exe fix generalized into the exe-alias architecture. Not yet verified against a real Apex launch — flagged as the one open follow-up. |
| 17 | **Claude Code adopted** as the primary hands-on tool, with a `CLAUDE.md` generated from this doc. **Apex fix confirmed live.** That test surfaced the **duplicate-game-name data corruption bug** — found, root-caused (catching a backwards first read from Claude Code in the process), and fixed with a real guard in `add_game()` plus a clear UI warning. **Then, the Call of Duty: Warzone investigation:** confirmed via Cloudflare's own published ranges that the old fallback endpoint was fake anycast, not real NA infrastructure. Discovered (via WHOIS on a publicly-available Call of Duty domain dataset) that CoD's real backend is Demonware, architecturally separate from Battle.net. Built a new standalone diagnostic tool, `trace_connections.py`, to trace a live game's real connections via `psutil`. Used it during a real Warzone match to find a consistent, non-CDN connection; verified via WHOIS that it's genuine Demonware infrastructure; verified via a real `tcp_ping()` call that it's reachable at a sane 248ms. Replaced the dead fallback with this confirmed-real address — explicitly **not** a full regional split, since Demonware doesn't expose fixed regional addresses the way Battle.net does. Updated `migrate_game_endpoints()` so existing installs get the fix too, catching and fixing two real bugs in the first proposed version (a staleness check that wouldn't have matched Warzone's actual bad IP, and a hardcoded `region_note` that would have mislabeled Warzone as "Steam servers") before anything was applied, plus a third subtler bug (a shared staleness check that would have falsely re-triggered on Warzone's own new correct address forever) caught in the corrected version. Verified `migrate_game_endpoints()`'s actual call site and save-triggering logic directly before approving the change. Two further instances of an AI agent's summary not matching literal content were caught and corrected this session, on top of the Apex one — now treated as a hard standing rule for the project, not a one-off lesson. Committed and pushed all of this session's fixes to GitHub; the actual version bump → tag → installer → itch.io release stays held until the rest of the v2.2.0 checklist is complete. |
| 18 | Apex Legends and Path of Exile endpoints audited using the proven `trace_connections.py` + WHOIS method. Apex: confirmed via literal `ping_game()` source that CDN-first ordering meant its ping had likely been measuring Akamai latency; replaced both old endpoints with a single WHOIS- and live-trace-confirmed AWS address; live verification then surfaced a bigger finding — Apex's matchmaking dynamically assigns datacenters per match, confirmed via direct in-game evidence (`us-east-1` vs `sa-east-1`), generalizing the same limitation already flagged for Warzone. Path of Exile: found the same CDN-shadowing pattern, fixed with a WHOIS-confirmed Google Cloud endpoint, and verified against two independent ground-truth numbers (an in-game gateway screenshot and live in-app testing) with the tightest margin of any fix this session; also fixed a stale `exe` value, which required extending `migrate_game_endpoints()` to support exe-field migrations — a capability that didn't exist before tonight. Also resolved the dev's "missing games" question: not a bug, just 15 of 21 default games sitting disabled in the dev's own `games.json`; all 21 set to enabled for ongoing testing. Both fixes committed and pushed individually; the version bump stays held until the rest of the v2.2.0 checklist is complete. |
| 19 | World of Warcraft endpoint DNS/WHOIS-checked (resolves to Google Cloud, Netherlands) — inconclusive without a live trace, since ownership data alone can't distinguish a real cloud-hosted Blizzard backend from a login-layer front, and the dev has no active WoW/Classic subscription to test further. Shipping v2.2.0 with the endpoint unchanged and unverified, relying on player error reports. No subscription bypass considered or attempted. Valorant also audited this session — live trace consistently showed only TCP traffic; root cause confirmed directly via raw `netstat` showing Valorant's UDP sockets have no recorded remote peer (`*:*`), meaning real match traffic uses unconnected UDP sockets invisible to any OS-connection-table tool, not a permissions/anti-cheat issue. Shipping Valorant's endpoints unchanged, documented as login/API latency only. Surfaced a third, distinct class of audit-blocking issue for the project, now a standing architecture fact. CS2 and Dota 2 also addressed this session: CS2 confirmed via live `netstat` trace to route through Valve's Steam Datagram Relay (SDR), which deliberately hides server IPs from clients as an anti-DDoS measure — a more specific, by-design root cause than Valorant's generic unconnected-UDP finding. Dota 2 documented by architectural inference only (dev doesn't own the game) given its shared Valve/Steamworks SDR foundation with CS2. Both ship with existing endpoints unchanged, already honestly labeled "Steam servers." League of Legends also audited this session — live `netstat` trace during an active ARAM confirmed the same unconnected-UDP wall as Valorant, this time via a two-process architecture (`LeagueClient.exe` handling CDN/chat, `League of Legends.exe` showing zero external TCP). Ships unchanged. Also flagged an open labeling-consistency question: Valorant's and LoL's `region_note` values may overstate what's actually measured, the same issue Apex's label had before Session 18's fix — not resolved this session. |
| 19 (follow-up) | Desk-only DNS/WHOIS audit of the remaining 11 default games (Fortnite, PUBG, FFXIV, Diablo IV, FIFA/EA FC, Rocket League, Minecraft, GTA Online, R6 Siege, Destiny 2, Lost Ark) — no live trace, no code changes, same treatment as WoW. Confirmed `api2.ea.com` is dead (NXDOMAIN) — flagged as a standalone fix. Found a list-order effect on Fortnite/Rocket League and R6 Siege where identical CDN-vs-real endpoint pairs win or lose purely based on which is listed first. FFXIV elevated to a stronger regional-split candidate after finding genuine named per-datacenter lobby servers (`neolobby06.ffxiv.com` for Chaos/EU) distinct from the currently-used global `frontier.ffxiv.com` — not yet verified or applied. Two new features scoped for later: an opt-in player report-system trace feature (fast-follow after v2.2.0) and a future personal-use-only JackalNode tool to automate the WHOIS/CDN filtering this audit required — the latter explicitly designed to be agent-operable for the dev's in-progress personal AI assistant. |
| 20 | **macOS Stage A test build completed and sent to a real tester.** Three fixes applied: corrected the `winreg` import guard in `game_detector.py` (platform check moved before any unguarded reference, not just the import line), added a darwin-only `BUNDLE()` block to `pingguard.spec`, then switched the darwin build from onefile to onedir mode after PyInstaller's own build log warned onefile clashes with macOS security. New manual-only workflow, `.github/workflows/build-macos-test.yml`, builds and zips a real `.app` via `ditto` and uploads it as a workflow artifact rather than a GitHub Release. Verified before sending: bundle structure (`Frameworks` folder present, confirming onedir took effect), sane size (~27MB), clean warning log, and the one remaining `winreg` reference in `app.py` confirmed already platform-gated. Packaging is verified; runtime on real hardware is not yet confirmed — awaiting the tester's report. **Separately, resolved a security incident:** the dev's PC had a genuine malware infection, unrelated to PingGuard/StartGuard. Full audit of both GitHub repos (commit history, workflows, `requirements.txt`, `updater.py`, `reporter.py`) found no tampering; fresh VirusTotal scans of both apps' real release installers came back clean apart from already-documented single-vendor heuristic false positives. No user-facing action needed; dev machine reinstalled, project folder survived intact on a separate drive, toolchain reconfigured. **New open issue surfaced:** a real user hit a PyInstaller onefile self-extraction crash (`Failed to load Python DLL`) immediately after a Windows auto-update — likely AV interference during temp-folder extraction, and architecturally the same onefile fragility just confirmed on macOS. Not yet root-caused; flagged as a real candidate for moving the Windows build to onedir too. |
| 21 | **Root-caused and fixed the Windows auto-update crash flagged in Session 20.** Full diagnostic pull from the affected user (Jason/CautionHeavy — Defender status, Controlled Folder Access log, orphaned `_MEI` folders) ruled out AV blocking specifically; root cause determined to be a timing/lock race during onefile's temp-folder extraction. **Migrated the Windows build from onefile to onedir**, mirroring the darwin `COLLECT()` pattern already proven in Session 20 — `pingguard.spec` and `PingGuard.iss` both updated and verified against real local builds before touching the cloud pipeline; `.github/workflows/build.yml` and `updater.py` both confirmed via full literal read to need zero changes. Verified extensively before shipping: local PyInstaller build, local Inno Setup compile, fresh-install test, and a real upgrade-path test (v2.2.0 onefile GitHub Release → new onedir installer) using a deliberate marker entry in `games.json` that survived the upgrade byte-for-byte — proving real user data isn't lost. Shipped as **v2.2.1**, tagged and built cleanly via GitHub Actions, held back from itch.io and sent directly to Jason first — **confirmed fixed on his actual affected machine.** Separately, the Mac tester's auto-updater surfaced a second, distinct bug: macOS has no Release asset to update to and `updater.py` has no platform-aware asset selection, so the update prompt fails to launch what it downloads. Diagnosed via Console log analysis (confirmed the tester's existing Stage A build itself is unaffected — this is purely an update-delivery gap). Deliberately not fixed this session — needs its own dedicated session rather than a rushed patch. Also surfaced: a retired pre-2.0 uninstaller (v1.5) deletes the shared `%APPDATA%\PingGuard` folder outright, a real cross-version data-loss risk for anyone with an old install lingering — documented, not fixed. LoL live-match ping verification data from an earlier session is presumed lost. Mac Stage A runtime confirmation still pending. |
| 22 | macOS auto-update bug fixed end-to-end: new `build-macos` job attaches a real asset to tagged Releases, `updater.py` rewritten platform-explicit. Verified via v2.2.2 pipeline release and a real Mac tester. Shipped as v2.2.2. Deferred: in-app licence link, version display in Settings. |
| 23 | In-app license viewer and Settings version/update-available indicator shipped as v2.2.3. `LICENSE.txt` created at project root (new file, UTF-8, title "JackalNode Licence" per the shared-text convention, £ symbol byte-verified) and bundled via `pingguard.spec`'s `datas`. `settings_dialog.py` gained `LicenseDialog`, `_license_path()`/`_load_license_text()` helpers, a "View License" button, a `version_label`, and a passive `UpdateCheckWorker` check for a quiet update-available indicator (separate from the existing startup `check_for_updates()` popup). Verified via dev run (both themes), a forced older-version test of the update indicator (reverted before commit), and a full PyInstaller build confirming `LICENSE.txt` landed in the onedir output. VirusTotal showed the same known Wacatac.B!ml + Arctic Wolf heuristic pair as prior releases — confirmed via matching file hash to be re-evaluation noise, not actioned. Committed as two separate commits, tagged v2.2.3, GitHub Actions green on both platform jobs, and itch.io manually updated to current for the first time since v2.2.0. New open items: StartGuard's `LICENSE.txt` still needs its title fixed to match; a non-fatal `QFont::setPointSize` console warning observed during theme testing, pre-existing, not investigated. |
| 24 | Triggered by real (secondhand) user reports that people couldn't add games back. Root-caused and fixed: `GameManager.add_game()` was rejecting any name match against `self._games` including disabled entries, and `enabled: False` is only ever set by the first-run wizard with no re-enable path anywhere in the app — meaning unchecking any of the 21 defaults during onboarding stuck it forever. Reproduced live (disabled GTA Online, confirmed the exact "already in your list" dead-end, fixed by re-enabling a disabled match instead of rejecting it), full regression-tested (case-insensitivity, real duplicates still blocked, new custom games unaffected, zero data loss on the re-enabled entry). Separately, replaced the header's generic controller emoji with a real transparent line-art version of the app's own shield/target logo (extracted from `assets/icon.ico`, matched to the app's accent color, rebuilt as line-art after the first pass's solid interior fill looked like an opaque box in light theme) — `pingguard.spec` updated so the new asset actually ships. Then closed out the Session 19 follow-up's `neolobby06.ffxiv.com` lead: WHOIS-confirmed (Square Enix CO LTD, Frankfurt), real port found via Square Enix's own documentation (54994, the only one of five documented ports that's actually reachable), live-verified via TCP + an independent ICMP baseline (161-162ms, both matching within a few ms) without needing an active subscription — evidence tier on par with the project's live-traced fixes despite that constraint. `games.py` and `migrate_game_endpoints()` both updated. New open item surfaced during the FFXIV work, not yet root-caused: `ping_engine.py` pings every enabled game in parallel with no throttling, likely self-inflicting jitter into readings app-wide (the same endpoint was rock-stable in isolation but swung 159-818ms inside a real all-games cycle). Three separate commits, each independently revertible. |
| 25 (unfinished — continued in Session 26) | Started as a "Riot status rework": Valorant/LoL's ping display replaced with a real Riot service-status check (green "Online" / amber "Game Server Unavailable") instead of TCP ping — the direct answer to Session 19's finding that TCP ping architecturally can't measure real match latency for either title. The chat that built this ran long and got compacted before the full diff was ever shown in this doc-writing session, so the exact code isn't confirmed from source here — only from a compacted summary and the resulting UI screenshots. Live testing by the dev on his real app surfaced two confirmed bugs, neither root-caused: row click-to-expand broken for Valorant/LoL, and "Your Region" had no effect on the status shown. Full detail in the dedicated Riot Status Check section above. |
| 26 | Picked up Session 25's handoff via Claude Code with real read access to the project folder. Both bugs root-caused from literal source: click-to-expand was a deliberate early-return in `GameRow.mousePressEvent()` for status rows (removed); the region bug was `check_riot_status()` reading one hardcoded `status_shard` with `user_region` never wired in (fixed via a per-region `status_shards` map, live-verified shard-by-shard against Riot's real status endpoints). Stress-tested whether a finer region split than the original 5 buckets would matter before building it — confirmed yes for Korea and Brazil (genuinely separate real Riot shards) but not for League's Asia-vs-Korea (no general APAC shard exists for League) — added Korea, Brazil, and Africa (the last already producible by the first-run wizard but silently unrecognized elsewhere) as explicit regions. `migrate_game_status_source()` rebuilt to patch existing installs; tested for idempotency. Verified end-to-end against real, independently-reconfirmed live Riot incidents (Valorant EU's Dubai/Bahrain outage, League Brazil's Gifts notice) rather than a clean-everywhere test — each surfaced only when its actual region was selected. |
| 27 | Root-caused and fixed the Session 24 ping-jitter open item. Two independent live test scripts (`jitter_test.py`, 30min interleaved A/B/C/D; `dns_isolation_test.py`, 25min DNS/HOST/IP isolation) directly disconfirmed the "unthrottled parallel pinging" theory — the exact `ping_all()` replica was consistently the cleanest tested condition — and instead isolated an OS DNS-cache-TTL-expiry cost landing on whichever call first touches a hostname after cache expiry (0/135 combined rounds showed a second call inherit a first call's spike). Fixed with a discard-first warm-up ping in `PingWorker._ping_one()`, chosen over an app-level IP cache specifically to avoid staleness risk for games with dynamic per-match server assignment (Warzone, Apex). Separately, at the dev's request, added a full pause of background pinging/notifications in `app.py`'s `_auto_tick()` while any monitored game is detected running, resuming automatically once it closes. Both live-verified in the real app (League of Legends and CS2, two different code paths) via internally-consistent countdown/timestamp checks across paired screenshots. A ~2-hour real background run showed FFXIV's chart tighten from the original 159-818ms-swinging description to 161-510ms across 60 samples — a large improvement, honestly not a full elimination (one residual spike, not investigated further). Committed as `0e86f4f` alongside the two new diagnostic scripts and pushed to `main`. Not yet tagged or built — this bundles with Sessions 24-26's still-unshipped fixes (add_game re-enable, header logo, FFXIV endpoint, Riot status check + region fix) into whatever the next release ends up being. |