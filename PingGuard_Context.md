# PingGuard — Context Document
> Paste alongside JackalNode_Context.md at the start of any PingGuard session — though as of Session 17, the primary working method has shifted (see Tooling section below).
> Built fresh in Session 12, modeled on StartGuard_Context.md's structure (StartGuard is the blueprint — see master doc Standing Rule #8).
> Last updated: Session 19 — Five games audited this session, all documentation-only (no code changes). WoW: DNS/WHOIS-checked, inconclusive. Valorant + League of Legends: confirmed architecturally blocked (unconnected UDP) — LoL's confirmation upgrades this from a Valorant one-off to a confirmed Riot company pattern. CS2: confirmed via live `netstat` trace, Valve SDR deliberately hides server IPs by design. Dota 2: inferred from CS2's SDR finding. See each game's dedicated section for full detail.

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

**Open consistency question flagged, not resolved this session:** both Valorant's and LoL's `region_note` values ("EU West" / "EUW") imply real match-server latency the same way Apex's old "EU servers" label did before Session 18's fix corrected it. Unlike CS2/Dota2's already-honest "Steam servers" label, these two arguably need the same precision pass Apex got. Not done this session — flagged for a quick follow-up decision whenever convenient, not blocking.

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
| `settings.py` | ✅ Updated (Session 17 & 18) | `add_game()` duplicate-name guard (Session 17). `migrate_game_endpoints()` Warzone and Apex Legends entries (Session 17/18); Path of Exile entry added, plus the function's apply loop extended to optionally write an `exe` field — the first exe-field migration capability in the codebase (Session 18). |
| `main_window.py` | ✅ Updated (Session 17) | `_on_add_game()` now checks `add_game()`'s return value and shows a `QMessageBox.warning` on a duplicate name. Confirmed it never reads `game["exe"]` directly. |
| `games.py` | ✅ Updated (Session 16, 17 & 18) | Apex Legends `exe` alias list (Session 16). Warzone endpoint fix (Session 17). Apex Legends `endpoints`/`region_note` fixed with a WHOIS- and live-trace-confirmed AWS address (Session 18). Path of Exile `endpoints` replaced with a WHOIS- and live-trace-confirmed Google Cloud address (`34.144.246.52:6112`); `region_note` corrected; `exe` updated to alias list `["PathOfExile.exe", "PathOfExileSteam.exe"]` (Session 18). |
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
- **New standing pattern (Session 18): `migrate_game_endpoints()`'s fix dict format extended to support an optional `'exe'` key, applied via a guarded line in the apply loop (`if 'exe' in fix: game['exe'] = fix['exe']`).** Confirmed this cannot affect any existing fix entry without that key. This is the first mechanism in the codebase for migrating a game's `exe` value on existing installs — previously only `endpoints` and `region_note` could be migrated.
- **Open question flagged (Session 18): Apex Legends's exe alias generalization (Session 16/17) was confirmed working live via real testing, but no corresponding `migrate_game_endpoints()` exe entry was ever added for it at the time — the capability didn't exist yet.** Worth confirming next session whether Apex's existing `games.json` entry already has the correct alias list (possibly written incidentally during the Session 17 duplicate-name manual merge) or whether it's relying on something else. Not urgent, but worth closing the loop now that the mechanism exists to actually fix it if needed.
- **New fact (Session 18): the "missing games" symptom reported by the dev was not a bug.** `_populate_games()` in `main_window.py` filters purely on a per-game `enabled` boolean (defaulting to `True` if missing) — confirmed via literal source, no category/search filtering exists. Only 6 of the 21 `DEFAULT_GAMES` entries were actually enabled in the dev's real `games.json` (Apex, Overwatch 2 EU/NA, World of Warcraft, League of Legends, Rainbow Six Siege). All 21 were set to enabled during this session to support ongoing endpoint-audit testing, and the dev intends to leave them enabled going forward — meaning PingGuard's monitoring loop is now actively pinging all 21 default games' endpoints on every cycle, not just 6.
- **New architecture fact (Session 19): three distinct classes of audit-blocking issue are now confirmed for this project** — (1) CDN-shadowing, a real correct address exists and just needs finding (Warzone/Apex/PoE); (2) dynamic per-match datacenter assignment, a real address exists but changes session to session (Warzone/Apex); (3) unconnected/`sendto()`-style UDP sockets, the OS itself never records a remote peer, making the address invisible to any connection-table tool regardless of permissions (Valorant, confirmed via raw `netstat`, independent of `psutil`/Vanguard). Check for class (3) early via `netstat`'s UDP remote-address column before investing in a full WHOIS pass.
- **Refinement to the Session 19 three-class framework: Valve's Steam Datagram Relay (SDR) is now a confirmed, specific instance of class 3 (unconnected UDP) for CS2, and almost certainly for Dota 2 by inference.** Unlike Valorant's case, SDR's IP-hiding isn't incidental netcode behavior — it's Valve's explicit, documented anti-DDoS design. Worth assuming by default for any Steamworks-API title going forward, rather than treated as a one-off. CS2 and Dota 2's existing `region_note` of "Steam servers" turned out to already be an honest label rather than something needing correction, unlike Warzone's old fallback.
- **Refinement to the Session 19 architecture findings: Riot's unconnected-UDP pattern (first confirmed on Valorant) now confirmed on League of Legends too** — a much older title on a completely different engine, run by the same company. Worth treating as a default assumption for any further Riot title, the same way Steam Datagram Relay is now assumed by default for Steamworks titles.

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
- ✅ Path of Exile endpoint audited and fixed (Session 18) — same CDN-shadowing pattern as Apex, fixed with a WHOIS-confirmed Google Cloud endpoint. Verified against two independent ground-truth numbers (in-game gateway screenshot showing 22ms, live in-app testing showing 27ms vs a 32ms in-game lobby reading) — tightest confirmation margin of any fix this session. Stale `exe` value (`PathOfExile.exe` vs the real `PathOfExileSteam.exe`) also fixed, which required extending `migrate_game_endpoints()` to support exe-field migrations for the first time.
- 🟡 World of Warcraft endpoint audited (Session 19) — DNS-resolved to Google Cloud, but ownership data alone can't confirm or rule out a real Blizzard backend. Live verification blocked by lack of an active subscription. Shipping as-is, unverified, relying on player error reports going forward.
- 🟡 Valorant endpoint audited (Session 19) — architecturally blocked, not fixable via this method: real-time gameplay data confirmed (via Riot's own port docs + raw `netstat`) to run over unconnected UDP sockets, invisible to any OS-connection-table-based tool. Shipping existing TCP-only endpoints unchanged, documented as login/API latency only.
- 🟡 CS2 endpoint audited (Session 19) — architecturally blocked, more specific root cause than Valorant: confirmed via live `netstat` trace that CS2 routes match traffic through Valve's Steam Datagram Relay (SDR), which deliberately hides server IPs from clients as an anti-DDoS measure. No real server IP is ever visible to any client-side tool, by design. Shipping existing endpoints unchanged — already honestly labeled "Steam servers," nothing to fix.
- 🟡 Dota 2 endpoint status documented (Session 19) — inferred, not directly traced (dev doesn't own the game). Same Valve/Steamworks SDR architecture as CS2, confirmed via Valve's own documentation that Dota 2 was SDR's original rollout testbed. Shipping existing endpoints unchanged on inferred grounds; flagged as the one audit this session not backed by a direct trace.
- 🟡 League of Legends endpoint audited (Session 19) — architecturally blocked, same wall as Valorant: confirmed via live `netstat` trace during an active ARAM match that the real game process (`League of Legends.exe`) has zero external TCP and only one unconnected UDP socket. The separate `LeagueClient.exe` process handles all visible CDN/chat traffic. Shipping existing endpoints unchanged, documented as account/API latency only. Confirms Riot's UDP architecture as a company-wide pattern, not a Valorant one-off. 11 default games remain unaudited beyond Warzone/Apex/PoE/WoW/Valorant/CS2/Dota 2/LoL.
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
- **Audit the other ~11 default games** for the same blended-region-fallback issue — `trace_connections.py` plus a WHOIS lookup on whatever address it surfaces is now the proven process; CoD Warzone is the worked example.
- **Audit the other ~11 default games for exe staleness** — lower priority, same "publisher renamed it" risk as Apex.
- **Whether `eu.battle.net` itself is measuring the right thing for Warzone** — flagged but not resolved this session. Since Warzone's real backend is Demonware, not Battle.net, the existing "real" half of its endpoint pair may only reflect login-service latency, not actual match-server latency. Worth a closer look before assuming Warzone's entry is now fully correct just because the fake half was replaced.
- **The GCP address on port 1119** (`35.204.122.188`) seen during the Warzone trace — port 1119 is the same port already used for WoW's real game-data endpoint elsewhere in `games.py`. Possibly a second legitimate Warzone-related server, not investigated further this session.
- **Real-time per-match server detection** — confirmed twice now (Warzone's Demonware backend, Apex's AWS multi-region matchmaking) that a single hardcoded endpoint can't represent "the server you'd actually play in" for titles with dynamic datacenter assignment. `trace_connections.py` already proves the underlying psutil-based detection works; turning it into a live, in-app feature (rather than a one-off research script) is the real fix, and now has direct evidence motivating it, not just a hunch. v3 scope.
- World of Warcraft (`eu.actual.battle.net:1119`) — DNS/ownership checked Session 19 (Google Cloud, Netherlands), inconclusive without a live trace; subscription required for that, not currently available. Shipping unverified, watching for player error reports.
- Valorant (`euw1.pvp.net:443` / `eu.api.riotgames.com:443`) — audited Session 19, confirmed architecturally blocked: real match traffic uses unconnected UDP sockets invisible to any connection-table tool. Shipping endpoints unchanged, documented as login/API latency only. Packet-capture-based detection (Wireshark) flagged as real future work, not pursued this session.
- CS2 (`steamcommunity.com:443` / `api.steampowered.com:443`) — audited Session 19 via live `netstat` trace, confirmed architecturally blocked: real match traffic routes through Valve's Steam Datagram Relay, which deliberately hides server IPs from any client-side tool. Shipping endpoints unchanged — already honestly labeled, nothing to fix.
- Dota 2 (`steamcommunity.com:443` / `api.steampowered.com:443`) — status documented Session 19 by architectural inference only (dev doesn't own the game); same Valve SDR foundation as CS2. Shipping unchanged. Lower evidence tier than the rest of this session's audits — worth a real trace if a Dota-2-playing tester ever becomes available.
- League of Legends (`euw1.api.riotgames.com:443` / `eu.api.riotgames.com:443`) — audited Session 19 via live `netstat` trace during an active ARAM match, confirmed architecturally blocked: real game process has zero external TCP, only one unconnected UDP socket, identical to Valorant's pattern. Shipping unchanged. Also surfaced an open question: both Valorant's and LoL's `region_note` values may be as misleading as Apex's old one was pre-fix — flagged for a possible follow-up labeling pass, not resolved.
- Confirm whether Apex Legends's `exe` alias (Session 16/17) ever actually reached the dev's `games.json` via a real migration, or whether it's relying on something else — now that an exe-migration mechanism exists (Session 18), worth a direct check.
- All 21 `DEFAULT_GAMES` entries are currently enabled in the dev's `games.json` (changed Session 18 for testing purposes, dev intends to leave as-is) — PingGuard is now actively monitoring all 21 endpoints every cycle, not just the original 6. Worth keeping in mind if performance or Discord-report noise comes up later.
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
| 18 | Apex Legends and Path of Exile endpoints audited using the proven `trace_connections.py` + WHOIS method. Apex: confirmed via literal `ping_game()` source that CDN-first ordering meant its ping had likely been measuring Akamai latency; replaced both old endpoints with a single WHOIS- and live-trace-confirmed AWS address; live verification then surfaced a bigger finding — Apex's matchmaking dynamically assigns datacenters per match, confirmed via direct in-game evidence (`us-east-1` vs `sa-east-1`), generalizing the same limitation already flagged for Warzone. Path of Exile: found the same CDN-shadowing pattern, fixed with a WHOIS-confirmed Google Cloud endpoint, and verified against two independent ground-truth numbers (an in-game gateway screenshot and live in-app testing) with the tightest margin of any fix this session; also fixed a stale `exe` value, which required extending `migrate_game_endpoints()` to support exe-field migrations — a capability that didn't exist before tonight. Also resolved the dev's "missing games" question: not a bug, just 15 of 21 default games sitting disabled in the dev's own `games.json`; all 21 set to enabled for ongoing testing. Both fixes committed and pushed individually; the version bump stays held until the rest of the v2.2.0 checklist is complete. |
| 19 | World of Warcraft endpoint DNS/WHOIS-checked (resolves to Google Cloud, Netherlands) — inconclusive without a live trace, since ownership data alone can't distinguish a real cloud-hosted Blizzard backend from a login-layer front, and the dev has no active WoW/Classic subscription to test further. Shipping v2.2.0 with the endpoint unchanged and unverified, relying on player error reports. No subscription bypass considered or attempted. Valorant also audited this session — live trace consistently showed only TCP traffic; root cause confirmed directly via raw `netstat` showing Valorant's UDP sockets have no recorded remote peer (`*:*`), meaning real match traffic uses unconnected UDP sockets invisible to any OS-connection-table tool, not a permissions/anti-cheat issue. Shipping Valorant's endpoints unchanged, documented as login/API latency only. Surfaced a third, distinct class of audit-blocking issue for the project, now a standing architecture fact. CS2 and Dota 2 also addressed this session: CS2 confirmed via live `netstat` trace to route through Valve's Steam Datagram Relay (SDR), which deliberately hides server IPs from clients as an anti-DDoS measure — a more specific, by-design root cause than Valorant's generic unconnected-UDP finding. Dota 2 documented by architectural inference only (dev doesn't own the game) given its shared Valve/Steamworks SDR foundation with CS2. Both ship with existing endpoints unchanged, already honestly labeled "Steam servers." League of Legends also audited this session — live `netstat` trace during an active ARAM confirmed the same unconnected-UDP wall as Valorant, this time via a two-process architecture (`LeagueClient.exe` handling CDN/chat, `League of Legends.exe` showing zero external TCP). Ships unchanged. Also flagged an open labeling-consistency question: Valorant's and LoL's `region_note` values may overstate what's actually measured, the same issue Apex's label had before Session 18's fix — not resolved this session. |

