# PingGuard — Context Document
> Paste alongside JackalNode_Context.md at the start of any PingGuard session — though as of Session 17, the primary working method has shifted (see Tooling section below).
> Built fresh in Session 12, modeled on StartGuard_Context.md's structure (StartGuard is the blueprint — see master doc Standing Rule #8).
> Last updated: Session 18 — Apex Legends's blended endpoint list audited using the same `trace_connections.py` + WHOIS methodology proven on Warzone. Confirmed a real, previously-invisible bug: the CDN entry listed first in Apex's endpoints was shadowing the actual game-server ping via `ping_game()`'s first-success-wins logic. Fixed and shipped. Live in-game testing then surfaced a more important finding: Apex's matchmaking dynamically assigns datacenters per match, the same way Warzone's Demonware backend does — confirmed this time with direct screenshot evidence (PingGuard reporting `us-east-1` while the game itself reported `sa-east-1`). Documented as a known, accepted limitation rather than something fixed today — real motivation for the v3 real-time server detection roadmap item.

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
- **Version:** v2.1.0 shipped and live. v2.2.0 (per-game region management) is **in progress, not yet shipped** — see Session 15/16/17 below for what's done vs. still open.
- **Platforms:** Windows (live). macOS / Linux — Beta builds existed in v2.0.4 but not yet rebuilt. See Open Questions.
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
- **Project path:** `C:\Users\natha\Desktop\Project\PingGuard v3\PingGuard`
- **PyInstaller output:** `dist\PingGuard.exe` inside project root
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

## File Inventory

| File | Status | Notes |
|------|--------|-------|
| `main.py` | ✅ Stable | Version `2.1.0`. AppUserModelID set before `QApplication` is created. |
| `app.py` | ✅ Reviewed Session 16, unchanged | Confirmed it never reads `game["exe"]` directly — only consumes `ping_worker.get_running_games()`. |
| `settings.py` | ✅ Updated (Session 17 & 18) | `add_game()` duplicate-name guard (Session 17). `migrate_game_endpoints()` Warzone entry (Session 17); Apex Legends entry added following the same per-game `is_stale`/`region_note` pattern, collision-checked against all existing entries before applying (Session 18). |
| `main_window.py` | ✅ Updated (Session 17) | `_on_add_game()` now checks `add_game()`'s return value and shows a `QMessageBox.warning` on a duplicate name. Confirmed it never reads `game["exe"]` directly. |
| `games.py` | ✅ Updated (Session 16, 17 & 18) | Apex Legends `exe` alias list (Session 16). Warzone endpoint fix (Session 17). Apex Legends `endpoints` replaced with WHOIS- and live-trace-confirmed AWS address (`100.50.20.250:9000`); `region_note` corrected from stale "EU servers" to "EA servers (US-East, AWS)" (Session 18). |
| `add_game_dialog.py` | ✅ Updated (Session 16), confirmed working Session 17 | Server Address field clarity fix: relabeled, tooltip added, explanatory hint added, dialog height bumped 520→555. |
| `game_detector.py` | ✅ Stable since Session 15 | Steam/Epic/Riot/Battle.net detection. |
| `reporter.py` | ✅ Stable since Session 15 | `send_game_request()` + `send_report()`. |
| `setup_wizard.py` | ✅ Reviewed Session 17, unchanged | Confirmed it does not call `GameManager.add_game()`. |
| `ping_engine.py` | ✅ Updated (Session 16), confirmed working live Session 17 | `get_process_names_for_game()` + `_as_list()` helper. `tcp_ping()` reused directly (unmodified) this session to verify Warzone's new Demonware endpoint — 248ms, successful, confirming the function works correctly against genuinely distant real infrastructure, not just the games already in `DEFAULT_GAMES`. |
| `trace_connections.py` | 🆕 New (Session 17) | Standalone diagnostic script, not part of the shipped app. Uses `psutil` to list a named running process's real active connections. Built to verify Warzone's real server; reusable for auditing any other game going forward, and serves as a working proof-of-concept for the previously-flagged "psutil-based Server Address auto-fill" idea. |
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
- **Standing pattern (Session 16): `exe` / `exe_mac` / `exe_linux` can be a single string or a list of accepted aliases.**
- **New standing pattern (Session 17): a game's name is its sole identity everywhere in this data model, and that is now actually enforced.** `GameManager.add_game()` refuses to add a game whose name already exists, returning `False` instead of silently appending.
- **New standing pattern (Session 17): any entry added to `migrate_game_endpoints()`'s `fixes` dict must carry its own `is_stale` check and its own `region_note` — never a shared/broad condition across multiple games.** A correct new address for one game can coincidentally collide with another game's old-bad-address prefix check (proven this session: Warzone's real `185.34.106.103` vs CS2/Dota2's old-bad `185.x` check).
- **New architecture fact (Session 17): Call of Duty's actual game servers run on Demonware (Activision's own networking subsidiary), confirmed via RIPE WHOIS — not Battle.net.** Battle.net is only the PC login/launcher layer for Activision titles, unlike genuine Blizzard titles where it is the real backend. Demonware does not appear to expose fixed, named regional addresses the way Battle.net does — matchmaking dynamically assigns datacenters, observed to vary. This is why a full Overwatch-2-style regional split isn't currently available for Warzone.
- **Process lesson, reinforced three times this session (Apex data, the Grep/edit-status mismatch, the `migrate_game_endpoints()` description): when an agent's claim about file or code content doesn't match — or hasn't yet been checked against — the literal content, ask for the literal content before proceeding.** This is now a hard standing rule for this project, not a one-off catch.
- **New architecture fact (Session 18), generalizing the Session 17 Warzone finding: dynamic per-match datacenter assignment is not Call-of-Duty-specific.** Confirmed directly via live in-game evidence on Apex Legends — PingGuard's verified, WHOIS-confirmed AWS endpoint (`us-east-1`) didn't match the in-game datacenter readout (`sa-east-1`) on a later match. Any title using cloud-hosted, matchmaking-assigned dedicated servers should be assumed to share this limitation by default during future audits, rather than treated as a special case to check for individually.

---

## Release Sequence — Roadmap

### v2.0.5 / v2.0.6 — Patch: Bug Fixes & Infrastructure Parity ✅ SHIPPED
### v2.1.0 — Icon Completion + Light/Dark Theme + Cleanup ✅ SHIPPED

### v2.2.0 — Minor: Per-Game Management 🟡 IN PROGRESS
*Moderate risk — touches the core data model and monitoring loop.*
- ✅ Add Game auto-detection (Steam/Epic/Riot/Battle.net)
- ✅ Region-separation architecture, migration, and wizard rebuild (Overwatch 2 as worked example)
- ✅ Add Game host-field clarity fix (Session 16)
- ✅ Apex Legends exe mismatch fixed + generalized into exe-alias architecture (Session 16/17)
- ✅ Duplicate-game-name data corruption bug found, root-caused, and fixed (Session 17)
- ✅ Call of Duty: Warzone's dead/fake fallback endpoint replaced with a verified real Demonware address, with a corresponding `migrate_game_endpoints()` fix for existing installs (Session 17) — **note: this is a verified endpoint correction, not a full regional split.** EU/NA separation for Warzone remains unavailable, not just undone, since Demonware doesn't expose fixed regional addresses the way Battle.net does.
- ✅ Apex Legends endpoint audited and fixed (Session 18) — CDN-shadowing bug fixed, endpoint replaced with WHOIS- and live-trace-confirmed AWS address. **Known accepted limitation, not fully resolved:** confirmed live that Apex's matchmaking assigns different datacenters per match, so the fixed endpoint is correct only when a match happens to land in the same region it was captured in. Same shape as Warzone's unresolved `eu.battle.net` question — real per-match server detection is v3 scope.
- 🔲 Audit remaining ~16 default games for the same blended-region issue — now with a proven method (`trace_connections.py` + WHOIS verification) to do it properly
- 🔲 Audit remaining default games for the same exe-staleness risk
- 🔲 Real per-game region management screen
- 🔲 Per-game ping thresholds (not started)
- 🔲 Real "edit an existing game" UI
- 🔲 Investigate building the psutil-based Server Address auto-fill into the actual Add Game dialog — `trace_connections.py` proved the underlying idea works, but real connection lists are noisy (up to 9 simultaneous connections in one observed session) and would need real filtering logic before going anywhere near the UI

> COMING SOON: Stop pinging Frankfurt when you're playing on Joburg servers.

### v2.3.0 — Minor (tentative): Game Search
*Only proceeds if a workable data source for game server info is confirmed.*

### v3.0.0 — Major: Network Diagnostics
*High risk — new engine, new permissions model, new UI surface. Dedicated session(s) only.*

---

## Still To Do / Open Questions
- **Audit the other ~16 default games** for the same blended-region-fallback issue — `trace_connections.py` plus a WHOIS lookup on whatever address it surfaces is now the proven process; CoD Warzone is the worked example.
- **Audit the other ~16 default games for exe staleness** — lower priority, same "publisher renamed it" risk as Apex.
- **Whether `eu.battle.net` itself is measuring the right thing for Warzone** — flagged but not resolved this session. Since Warzone's real backend is Demonware, not Battle.net, the existing "real" half of its endpoint pair may only reflect login-service latency, not actual match-server latency. Worth a closer look before assuming Warzone's entry is now fully correct just because the fake half was replaced.
- **The GCP address on port 1119** (`35.204.122.188`) seen during the Warzone trace — port 1119 is the same port already used for WoW's real game-data endpoint elsewhere in `games.py`. Possibly a second legitimate Warzone-related server, not investigated further this session.
- **Real-time per-match server detection** — confirmed twice now (Warzone's Demonware backend, Apex's AWS multi-region matchmaking) that a single hardcoded endpoint can't represent "the server you'd actually play in" for titles with dynamic datacenter assignment. `trace_connections.py` already proves the underlying psutil-based detection works; turning it into a live, in-app feature (rather than a one-off research script) is the real fix, and now has direct evidence motivating it, not just a hunch. v3 scope.
- Path of Exile (`45.33.26.109:20481`) and World of Warcraft (`eu.actual.battle.net:1119`) remain unaudited — Apex was completed this session, these two are next using the same proven method.
- **Real per-game region management UI** — doesn't exist yet.
- **Real "edit existing game" UI** — confirmed not to exist anywhere in the app.
- **Server Address auto-fill for unlisted games** — `trace_connections.py` proves the psutil approach is viable in principle; building real filtering logic into the actual Add Game dialog is still future work.
- **macOS / Linux builds** — pipeline only builds Windows now.
- **Confirm workable game-server-info lookup source** before committing v2.3.0 as a real release vs. dropping it.
- **Decide scapy vs. manual raw sockets** for v3.0.0.
- **Tray icon cosmetic mismatch** — still shows a generic blue circle, not the shield art. Dev's call to leave as-is, low priority.

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
| 18 | Apex Legends endpoint audited using the proven `trace_connections.py` + WHOIS method. Confirmed via literal `ping_game()` source that CDN-first ordering meant Apex's ping had likely been measuring Akamai latency, not the game server. Replaced both old endpoints with a single WHOIS- and live-trace-confirmed AWS address; fixed the stale `region_note` in the same edit. `migrate_game_endpoints()` updated and collision-checked against all existing entries before applying — no repeat of Warzone's cross-game collision bug. Live verification then surfaced a more important finding than the fix itself: in-game data confirmed Apex's matchmaking dynamically assigns datacenters per match, the same pattern already flagged for Warzone — now backed by direct evidence rather than inference. Documented as a known, accepted limitation and folded into the v3 roadmap rationale rather than chased further this session. |

