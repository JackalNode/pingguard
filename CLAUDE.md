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

- **Version:** v2.2.2 shipped (macOS auto-update fix, verified end-to-end on real hardware). itch.io still serving v2.2.0 — general release pending. v2.3.0 not yet started — see roadmap.
- **Platform:** Windows and macOS both in production as of Session 22 — `build.yml` has a tag-triggered `build-macos` job (`needs: build`) that attaches a real macOS Release asset alongside the Windows installer. macOS Stage A packaging (Session 20) and full auto-update runtime (Session 22) are both confirmed on real hardware by a real tester. Linux has no test build of any kind yet.
- **Windows build format:** onedir as of v2.2.1 (was onefile through v2.2.0) — see dedicated section below.
- **Live on:** `jackalnode.itch.io/pingguard` and `github.com/JackalNode/pingguard`
- **CI/CD:** GitHub Actions — tag push → cloud build → installer attached to release automatically.
- **Auto-update:** wired via `updater.py`.
- **Process detection:** confirmed working live (Session 17) — Apex Legends "Running" bar and ping history both updated correctly during a real launch.
- **`trace_connections.py` (Session 17):** standalone script (not part of the shipped app) that uses `psutil` to list a running game's real active network connections. Built to verify Warzone's server address; reusable for auditing any other game, and a proof-of-concept for the psutil-based Server Address auto-fill idea.
- **All 21 `DEFAULT_GAMES` entries are currently enabled** in the dev's `games.json` (set Session 18 for endpoint-audit testing; dev intends to leave as-is).
- **All 21 default games audited across Sessions 18–19 + follow-up.** Warzone, Apex, and PoE: CDN-shadowing fixed with verified endpoints. WoW: inconclusive (no active subscription). Valorant, LoL: architecturally blocked (unconnected UDP, Riot company-wide pattern). CS2, Dota 2: architecturally blocked (Valve SDR deliberately hides server IPs). Remaining 11: desk-audited (DNS/WHOIS only, no code changes). `api2.ea.com` (FIFA/EA FC) confirmed dead and removed.

---

## Project Paths

- **Project root:** `E:\Projects\PingGuard v3\PingGuard` (confirmed Session 21 — the project lives on a separate physical drive from the OS, which is why it survived the Session 20 machine reinstall intact).
- **Local Python:** `C:\Python314\python.exe` (confirmed Session 21). The `python`/`python3` commands on PATH resolve to the Microsoft Store alias stub, not a real interpreter, and will error — always use the `py` launcher or this direct path.
- **Local Inno Setup:** `C:\Users\natha\AppData\Local\Programs\Inno Setup 6\ISCC.exe` (v6.7.3, per-user install, confirmed Session 21). Differs from GitHub Actions' cloud runner path (`C:\Program Files (x86)\Inno Setup 6\ISCC.exe`, hardcoded in `build.yml`) — both correct for their own environment, not a conflict.
- **All source files** sit flat in the project root — no `core/` or `src/` subfolder.
- **PyInstaller output (platform-dependent since Session 21's onedir migration):** Windows → `dist\PingGuard\` folder (`PingGuard.exe` + `_internal\`), no longer a single `dist\PingGuard.exe` file. macOS → `dist\PingGuard.app` (via the darwin `BUNDLE()` step, unchanged).
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
- **The `fixes` dict format supports two optional migration keys beyond `is_stale`/`endpoints`/`region_note`:** `'exe'` (Session 18) migrates a game's exe alias list; `'region_note_stale'` (Session 19) is a lambda checked against the game's current `region_note` — if it matches, `region_note` is updated to the entry's `region_note` value. Both are guarded in the apply loop; entries without either key are provably unaffected. The `is_stale` check is also now guarded (`'is_stale' in fix`) so entries that only carry `region_note_stale` (Valorant, LoL) don't crash the loop.

### Call of Duty / Demonware architecture
- **Call of Duty's actual game servers run on Demonware (Activision's own networking subsidiary), confirmed via RIPE WHOIS — not Battle.net.** Battle.net is only the PC login/launcher layer for Activision titles. For genuine Blizzard titles (Overwatch, Diablo, WoW), Battle.net *is* the real backend — this distinction matters when choosing what to ping.
- Demonware does not appear to expose fixed, named regional addresses the way Battle.net does. Matchmaking dynamically assigns datacenters. This is why a full Overwatch-2-style regional split isn't currently available for Warzone.
- The proven method for auditing any game's real server: run `trace_connections.py` during a live session, identify stable non-CDN ESTABLISHED connections, run WHOIS to confirm ownership, then verify via `tcp_ping()` before touching any code. A suspiciously low result (like 7ms from Cape Town to a "distant" server) means CDN/anycast — not a real datacenter.

### Dynamic datacenter assignment (Session 18 — generalizes Warzone finding)
- **Dynamic per-match datacenter assignment is not Call-of-Duty-specific.** Confirmed directly via live in-game evidence on Apex Legends: PingGuard's verified, WHOIS-confirmed AWS endpoint (`us-east-1`) didn't match the in-game datacenter readout (`sa-east-1`) on a later match.
- Any title using cloud-hosted, matchmaking-assigned dedicated servers should be assumed to share this limitation by default during future audits, rather than treated as a special case to check for individually.
- A single hardcoded endpoint is still a strict improvement over CDN-shadowed numbers — it will read correctly when a match lands in the same region. Solving it properly requires real-time per-match server detection (v3 scope).
- **Path of Exile does NOT share this problem** — PoE's gateway is a manual, persistent player choice rather than matchmaking-assigned, making it a real candidate for an Overwatch-2-style regional split in the future.

### Three classes of audit-blocking issue (Session 19 — standing architecture fact)
- **(1) CDN-shadowing** — a real correct address exists but is shadowed by a CDN endpoint that wins first-success-wins. Fixable via `trace_connections.py` + WHOIS (Warzone/Apex/PoE pattern).
- **(2) Dynamic per-match datacenter assignment** — a real address exists but changes session to session. Best-effort fix with a single confirmed address; real fix is v3 real-time detection (Warzone/Apex).
- **(3) Unconnected/`sendto()`-style UDP** — the OS itself never records a remote peer address. Invisible to all connection-table tools (`trace_connections.py`, `netstat`) regardless of permissions. Only viable path is packet capture (Wireshark). Confirmed on Valorant via raw `netstat` (`*:*` remote), independent of Vanguard.
- **Early detection shortcut for class 3:** check `netstat`'s UDP remote-address column. `*:*` remote = sendto()-style UDP = skip connection-table approach entirely.
- **Valve's Steam Datagram Relay (SDR) is a confirmed specific instance of class 3** for CS2 (live-traced), almost certainly Dota 2 by inference. Unlike Valorant, SDR's IP-hiding is explicit documented anti-DDoS design — no client-visible server IP exists at all, by intent. Assume SDR for any Steamworks-API title by default going forward.
- **Riot's unconnected-UDP pattern is confirmed company-wide**, not Valorant-specific: confirmed on League of Legends (live-traced, active ARAM match, distinct two-process architecture). Assume by default for any further Riot title.

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

## Path of Exile — Endpoint Fix (Session 18)

**What was wrong:** the entry blended `www.pathofexile.com:443` (Akamai CDN — same shadowing pattern as Apex) with `45.33.26.109:20481`. The CDN entry listed first was winning every ping via `ping_game()`'s first-success-wins logic. Additionally, the `exe` field was `"PathOfExile.exe"` (single string) — the actual running process is `PathOfExileSteam.exe`.

**How the replacement was found:** `trace_connections.py` run 5 times during a live session. Exactly two `ESTABLISHED` connections in every run: `34.144.246.52:6112` (non-standard port — real game traffic) and `2.16.199.16:443` (Akamai CDN). WHOIS on `34.144.246.52`: Google LLC (`GOOGL-2`), block `34.128.0.0/10`, confirmed Google Cloud customer use. WHOIS on `2.16.199.16`: Akamai (`AKAMAI-PA`) — confirms CDN-shadowing pattern identical to Apex.

**Verified against two independent ground-truth numbers:** `tcp_ping()` to `34.144.246.52:6112` returned 32ms; in-game gateway screenshot showed "South Africa" at 22ms (TCP SYN vs. UDP gap accounts for the difference). After applying the fix and relaunching, live in-app testing showed PingGuard reporting 27ms vs. an in-game lobby reading of 32ms — 5ms gap, tightest confirmation margin of any fix this session.

**What was fixed:**
1. `games.py`: `endpoints` replaced with `{"host": "34.144.246.52", "port": 6112}`. `region_note` corrected from `"EU servers"` to `"South Africa servers (Google Cloud)"`. `exe` updated to `["PathOfExile.exe", "PathOfExileSteam.exe"]` (alias list).
2. `settings.py` `migrate_game_endpoints()`: new `'Path of Exile'` entry added (own `is_stale`, own `region_note`, plus `'exe'` key to migrate the alias list to existing installs).
3. **New capability:** `migrate_game_endpoints()`'s apply loop extended with `if 'exe' in fix: game['exe'] = fix['exe']` — the first exe-field migration mechanism in the codebase. Guarded so existing fix entries without an `'exe'` key are unaffected.

**PoE does not have the dynamic-datacenter problem** — the gateway is a manual, persistent player choice. This makes it a future candidate for an Overwatch-2-style regional split (trace once per gateway the player manually switches to).

---

## CS2 — Endpoint Audit (Session 19, architecturally blocked — Steam Datagram Relay)

Live `netstat` during a live official matchmaking Deathmatch showed 53 UDP sockets, all `*:*` remote, zero TCP. Root cause is more specific than Valorant's: Valve's CS2 client routes all match traffic through Steam Datagram Relay (SDR), which deliberately hides server IPs from clients as an anti-DDoS measure — confirmed via Valve's own public SDR docs. Before matchmaking completes, the client fans out UDP probes across 49+ SDR relay PoPs to measure latency to each (explaining the high socket count). Once connected, the address is an internal token (`[A:n:nnnnnnnn]`), not an IP:port. No client-side tool can see a real server IP — by design. Existing endpoints unchanged; `region_note` of "Steam servers" was already honest.

---

## Dota 2 — Endpoint Status (Session 19, inferred — not directly traced)

Not live-traced; dev doesn't own Dota 2. Documented by architectural inference: Dota 2 is built on the same Valve/Steamworks foundation as CS2, and Valve's SDR rollout docs confirm Dota was SDR's original proving ground before CS:GO. Shipping existing endpoints unchanged on inferred grounds — lower evidence tier than the rest of this session's audits, flagged explicitly. Worth a real trace if a Dota-2-playing tester becomes available.

---

## League of Legends — Endpoint Audit (Session 19, architecturally blocked)

Live `netstat` during an active ARAM match. Two separate processes: `LeagueClient.exe` (lobby/launcher) and `League of Legends.exe` (in-match game). `LeagueClient.exe` external connections: two Cloudflare addresses on 443 (CDN/account) + one AWS Frankfurt on port 2099 (Riot RTMPS chat/presence). `League of Legends.exe`: zero external TCP, one unconnected UDP socket (`*:*`) — identical fingerprint to Valorant. Confirms Riot's unconnected-UDP pattern is company-wide, not Valorant-specific. Shipping unchanged. **Resolved, same session:** both Valorant's and LoL's `region_note` values were corrected to "Riot account/API layer (not match server)" via a new `region_note_stale` migration entry in `settings.py` (separate from the existing `is_stale` mechanism, so the other 5 entries are unaffected). Applied to `games.py` for fresh installs and confirmed firing correctly on the dev's existing `games.json`.

---

## World of Warcraft — Endpoint Audit (Session 19, inconclusive)

DNS-resolved `eu.actual.battle.net` → `34.141.148.228` (Google Cloud, europe-west4, Netherlands). Google Cloud ownership is not evidence of a fake endpoint — PoE's confirmed real server is also Google Cloud. Live trace blocked: no active WoW or WoW Classic subscription. No subscription bypass attempted. Shipping v2.2.0 with `eu.actual.battle.net:1119` unchanged, documented as unverified, relying on Discord error reports for real-world feedback. Retail WoW has a free trial path (Starter Edition, levels 1–20) for future verification. Open question: whether the single "World of Warcraft" entry should eventually split into retail/Classic (they likely diverge at the real realm-server level).

---

## Valorant — Endpoint Audit (Session 19, architecturally blocked)

Existing endpoints (`euw1.pvp.net:443`, `eu.api.riotgames.com:443`) are account/API layer, not match servers. Live traces (5 runs across 2 sessions) showed only TCP 443 + XMPP port 5223 — no gameplay traffic. Riot's published port docs confirm real match data runs on UDP 7000–8000. Root cause confirmed via raw `netstat` (independent of psutil/Vanguard): Valorant's two open UDP sockets show `*:*` as remote address — unconnected (`sendto()`-style) UDP, so the OS never records the real server IP. Invisible to all connection-table tools regardless of permissions. Shipping endpoints unchanged, documented as login/API latency only. Packet-capture (Wireshark) is the only viable next step — flagged as future work, not pursued this session.

---

## macOS Stage A Test Build (Session 20)

**Goal:** get a real `.app` onto a tester's Mac to start closing the macOS gap — Stage A only (package + launch), not a full feature-parity pass.

**Three fixes applied to support the build:**
1. **`game_detector.py`:** guarded the `winreg` import — the platform check was moved to before *any* unguarded reference to `winreg`, not just wrapping the `import` line itself. An import-only guard would still crash on non-Windows if any code path referenced `winreg` before the platform check ran.
2. **`pingguard.spec`:** added a `darwin`-only `BUNDLE()` block so PyInstaller produces a real `.app` bundle on macOS instead of a bare executable.
3. **Follow-up, same session:** switched the darwin build from `onefile` to `onedir` mode after PyInstaller's own build log warned that onefile mode clashes with macOS security. Windows build is untouched — still onefile.

**New file:** `.github/workflows/build-macos-test.yml` — manual `workflow_dispatch` only (not part of the tag-triggered release pipeline), runs on `macos-14` (Apple Silicon), builds via PyInstaller, zips the `.app` with `ditto`, uploads as a workflow artifact rather than attaching to a GitHub Release.

**Verified before sending to the tester:**
- `.app` bundle structure correct — `Frameworks` folder present, confirming `onedir` mode actually took effect.
- Size sane (~27MB).
- `warn-pingguard.txt` checked — only expected/harmless missing-module warnings.
- The one `winreg` reference in `app.py` confirmed safely platform-gated, not a second unguarded import site.

**Status: sent to tester**, along with a plain-English "how to open + what to test" guide. **Not yet confirmed to run correctly end-to-end on real hardware** — only confirmed to package correctly. Awaiting the tester's actual usage report.

---

## Windows Onedir Migration — Auto-Update Crash Fixed (Session 21)

**The bug:** a real user (Jason/CautionHeavy) hit `Failed to load Python DLL ... python311.dll ... module could not be found` immediately after auto-update fetched a new version and prompted to launch (originally reported Session 20).

**Root cause, confirmed via a full diagnostic pull from the affected user** (Windows Security/Defender status, Controlled Folder Access log, orphaned `_MEI` temp-extraction folders): zero Defender detections or CFA blocks against PingGuard — ruling out AV *blocking*. Actual cause is a timing/lock race during onefile's temp-folder extraction on every launch (real-time AV scanning holding a lock on `python311.dll` at the exact moment the bootloader tries to load it), not a targeted quarantine. Same underlying onefile fragility already confirmed on macOS (Session 20), different OS-specific trigger.

**The fix:** migrated the Windows build from onefile to onedir, mirroring the existing darwin `COLLECT()` pattern:
1. `pingguard.spec` — new `elif sys.platform == 'win32':` branch added. `exclude_binaries` and the `a.binaries`/`a.datas` exclusion widened from darwin-only to `('darwin', 'win32')`. Darwin block itself untouched.
2. `PingGuard.iss` — `[Files]` section's Windows source changed from a single named file to a recursive wildcard (`dist\PingGuard\*`, `recursesubdirs createallsubdirs`) to package the full onedir folder output. `MyAppVersion` bumped 2.2.0 → 2.2.1.
3. `main.py` — version bumped to 2.2.1.
4. **`.github/workflows/build.yml` and `updater.py` required zero changes** — confirmed via full literal review. The workflow only orchestrates PyInstaller/Inno Setup generically (already onedir-agnostic); `updater.py` only ever hands off to the Inno Setup installer via `subprocess.Popen`, never touches individual files itself.

**Verified before shipping:** local PyInstaller build (real onedir structure), local Inno Setup compile, fresh-install test (clean launch, correct `%APPDATA%` layout, real ping cycles), and a real upgrade-path test — installed the actual v2.2.0 onefile GitHub Release asset as a baseline, added a deliberate marker entry (`ZZZ_UPGRADE_TEST_MARKER`) to `games.json`, then upgraded to the new onedir installer. Marker survived byte-for-byte, confirming real user data isn't lost on upgrade.

**Shipped as v2.2.1**, tagged and built cleanly via GitHub Actions. Held back from itch.io and sent directly to Jason first — **confirmed fixed on his actual affected machine.** itch.io upload still pending as of end of Session 21.

**Side findings, not yet acted on:**
- A retired pre-2.0 PingGuard uninstaller (v1.5, predates this repo's git history) deletes `%APPDATA%\PingGuard` outright on uninstall. Since that folder is shared across all versions via Qt's org/app name resolution, any user with an old pre-2.0 install alongside a current one risks the old uninstaller wiping current save data. Not fixed — flagged for whenever legacy-install cleanup gets attention.
- League of Legends live-match ping verification data (real in-match cross-checks from an earlier session) is presumed lost — no longer reproducible from current chat/session history. Flag as needing re-verification whenever LoL endpoint work is revisited; not currently treated as still-confirmed.

---

## macOS Auto-Update — Fixed End-to-End (Session 22)

**The bug (Session 21):** the Mac tester running the Session 20 Stage A build received a "v2.2.1 available" update prompt and hit "Download complete but installer could not launch." Root cause was two-part: `build.yml` never attached a macOS asset to real Releases, and `updater.py`'s `_find_installer_url()` had no platform awareness — it grabbed the first Release asset ending in `.exe` regardless of OS.

**The fix, applied Session 22:**
1. **`build.yml`:** new `build-macos` job, `runs-on: macos-14`, sequenced via `needs: build` (no race condition with the Windows job). Builds via PyInstaller, zips the `.app` with `ditto`, and attaches `PingGuard_v{version}_macOS.zip` to the same tagged Release via `softprops/action-gh-release@v2`. Fires on the same tag trigger as the Windows job (`v[0-9]*.[0-9]*.[0-9]*`) — one `on:` block covers both jobs.
2. **`updater.py`:** rewritten to be platform-explicit throughout — `_find_installer_url()` branches on `sys.platform` (`win32` → first `.exe` asset, `darwin` → first `.zip` asset containing `"macos"`, anything else → empty string, i.e. fails closed). `_start_download()` derives the file extension per platform. `_on_download_done()` is a clean win32/darwin two-way branch — Windows launches the installer via `subprocess.Popen` and exits; macOS shows a manual "drag to Applications" dialog instead (no silent launch attempt). `check_failed` signal now carries a reason string (`"error"` | `"no_asset"`) instead of firing blind.
3. **`reporter.py`:** new `send_update_report()`, mirroring `send_game_request()`'s pattern — powers a "Report an Issue" button surfaced from both the macOS manual-update dialog and the "no matching asset" failure dialog.

**Verified:** a dedicated v2.2.2 pipeline-test release — both `build` and `build-macos` jobs green, both assets confirmed present on the Release — and confirmed working end-to-end by a real Mac tester after a one-time manual bootstrap onto the new build.

**Deferred, not part of this fix:** in-app licence link (StartGuard already has the pattern), and displaying current version + update-available indicator in Settings.

---

## Security Incident — Resolved (Session 20)

Nathan's dev PC had a genuine malware infection, unrelated to PingGuard or StartGuard. Full audit of both GitHub repos (commit history, workflow files, `requirements.txt`, `updater.py`, `reporter.py`) found no tampering. Fresh VirusTotal scans of both apps' actual release installers came back clean apart from well-documented single-vendor heuristic false positives (`Wacatac.B!ml` on PingGuard, a generic low-signal flag on StartGuard) — the same known PyInstaller false-positive pattern already documented in this project. No user-facing action was needed. The local dev machine was reinstalled; the project folder survived intact on a separate drive; the toolchain (git, Claude Code) was reinstalled and reconfigured.

---

## File Inventory

| File | Notes |
|------|-------|
| `main.py` | Version string `2.2.2` (bumped Session 22). AppUserModelID set before QApplication. |
| `app.py` | Never reads `game["exe"]` directly — only consumes `ping_worker.get_running_games()`. |
| `main_window.py` | `_on_add_game()` checks `add_game()` return value; shows warning on duplicate. Never reads `game["exe"]` directly. `_populate_games()` filters on `enabled` boolean only — no category or search filtering. |
| `settings.py` | `GameManager`. `add_game()` enforces unique names (case-insensitive), returns True/False. `migrate_game_endpoints()` restructured: each entry in `fixes` carries its own `is_stale` lambda and `region_note` — CS2, Dota 2, Call of Duty: Warzone, Apex Legends, Path of Exile, Valorant, and League of Legends all present. Apply loop optionally writes `exe` when the fix dict carries an `'exe'` key (Session 18); optionally updates `region_note` when the fix dict carries a `region_note_stale` lambda that matches the current value (Session 19) — both guarded, existing entries without those keys are unaffected. `migrate_game_regions()` unchanged. `update_game()` exists but has no UI caller. |
| `games.py` | `DEFAULT_GAMES`. Apex exe is `["r5apex.exe", "r5apex_dx12.exe"]`. Apex endpoint is `100.50.20.250:9000` (WHOIS-confirmed AWS/EA, region_note "EA servers (US-East, AWS)"). OW2 split into (EU)/(NA). Warzone second endpoint is `185.34.106.103:3074` (confirmed Demonware). Path of Exile endpoint is `34.144.246.52:6112` (WHOIS-confirmed Google Cloud, region_note "South Africa servers (Google Cloud)"); exe is `["PathOfExile.exe", "PathOfExileSteam.exe"]`. Valorant and League of Legends region_note corrected to "Riot account/API layer (not match server)" (Session 19). |
| `ping_engine.py` | `get_process_names_for_game()` + `_as_list()` helper. `check_running_games()` matches alias-set overlap. `tcp_ping()` reused directly to verify Warzone, Apex, and PoE endpoints. `ping_game()` is first-success-wins — walks endpoints in order, returns on first success. |
| `game_detector.py` | Scans Steam/Epic/Riot/Battle.net for installed games. All detectors independently try/except. `winreg` import guarded behind a platform check placed before any unguarded reference (Session 20, macOS build support). |
| `add_game_dialog.py` | Detected-games dropdown, Browse button, game-request report hook. Dialog height 420×555. Server Address field has label, tooltip, and hint. All confirmed working via live testing. |
| `reporter.py` | `send_report()` + `send_game_request()` + `send_update_report()` (Session 22, line 121) — mirrors `send_game_request()`'s pattern, no game dependency, powers the "Report an Issue" button in the update-flow dialogs. Webhook from `constants.py`. |
| `setup_wizard.py` | First-run wizard. Region step before games step. AWS endpoints for latency probing. Does not call `add_game()`. |
| `theme.py` | Dark/light token dicts. Stable since Session 14. |
| `logger.py` | CSV session logging, 30-day auto-cleanup. Discovered Session 15, not modified. |
| `trace_connections.py` | Standalone diagnostic script — not part of the shipped app. Uses `psutil` to list a named running process's active connections. Built for Warzone endpoint verification; reusable for any game audit going forward. |
| `constants.py` | Discord webhook (gitignored). |
| `updater.py` | Auto-update shared logic. Needed zero changes for the Windows onedir migration (Session 21). **Rewritten platform-explicit (Session 22):** `_find_installer_url()` branches on `sys.platform` (win32/darwin/fails-closed empty string); `_start_download()` derives extension per platform; `_on_download_done()` is a clean win32/darwin two-way branch; `check_failed` signal now carries a reason (`"error"`/`"no_asset"`). |
| `pingguard.spec` | darwin-only `BUNDLE()` added; darwin build mode switched onefile → onedir (Session 20). **Windows now also onedir (Session 21):** new `elif sys.platform == 'win32':` branch mirrors the darwin `COLLECT()` pattern; `exclude_binaries` and the binaries/datas exclusion widened from darwin-only to `('darwin', 'win32')`. |
| `PingGuard.iss` | **Updated Session 21:** `[Files]` section's Windows source changed from a single named file to a recursive wildcard (`dist\PingGuard\*`, `recursesubdirs createallsubdirs`) to package the full onedir output. `MyAppVersion` bumped 2.2.0 → 2.2.1. |
| `.github/workflows/build-macos-test.yml` | New (Session 20). Manual `workflow_dispatch` only, macos-14 runner, builds + zips `.app` via `ditto`, uploads as a workflow artifact — not part of the tag-triggered release pipeline. Superseded for real releases by `build.yml`'s `build-macos` job (Session 22), but left in place as a standalone manual test workflow. |
| `.github/workflows/build.yml` | **Updated Session 22:** new `build-macos` job (`runs-on: macos-14`, `needs: build`) added alongside the existing Windows `build` job. Same single tag trigger (`v[0-9]*.[0-9]*.[0-9]*`) covers both. Zips the `.app` via `ditto` and attaches `PingGuard_v{version}_macOS.zip` to the Release via `softprops/action-gh-release@v2`. |

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

## Roadmap

| Version | Status | Description |
|---|---|---|
| v2.0.5 / v2.0.6 | ✅ Shipped | Bug fixes, infrastructure parity |
| v2.1.0 | ✅ Shipped | Icon, light/dark theme, Settings cleanup |
| v2.2.0 | ✅ Shipped | Per-game region management, full 21-game endpoint audit, exe staleness check |
| v2.2.1 | ✅ Shipped (GitHub only — itch.io pending) | Windows onedir migration, fixes onefile self-extraction auto-update crash |
| v2.2.2 | ✅ Shipped (GitHub only — itch.io pending) | macOS auto-update fixed end-to-end — tag-triggered `build-macos` job + platform-explicit `updater.py` rewrite, verified on real hardware |
| v2.3.0 | Tentative | Game search / server auto-fill — psutil approach is the leading candidate; only proceeds if a workable implementation is confirmed |
| v3.0.0 | Future | Network diagnostics: traceroute, hop latency, ISP ID, packet loss. Real-time per-match server detection is a confirmed motivation (dynamic datacenter assignment observed on both Warzone and Apex). Elevation approach (scapy vs. raw sockets) not yet decided. |

---

## Open Questions

- **✅ FIXED (Session 21) — Windows auto-update crash.** Root-caused (AV lock-race during onefile temp-folder extraction, not AV blocking) and fixed by migrating the Windows build to onedir. Shipped as v2.2.1, confirmed fixed on the affected user's real machine. See dedicated section above.
- **✅ FIXED (Session 22) — macOS auto-update.** `build.yml`'s new `build-macos` job now attaches a real Release asset; `updater.py` rewritten platform-explicit, fails closed for unrecognized platforms. Shipped as v2.2.2, verified via a real pipeline-test release and confirmed end-to-end by a real Mac tester. See dedicated section above. Deferred: in-app licence link, version display in Settings.
- **Legacy pre-2.0 uninstaller data-loss risk (surfaced Session 21, not fixed):** a retired v1.5 uninstaller deletes the shared `%APPDATA%\PingGuard` folder outright, which could wipe a current install's data if an old install is still lingering on a user's machine.
- **LoL live-match ping verification data presumed lost (Session 21)** — earlier in-match cross-check numbers are no longer reproducible from session history; needs re-verification whenever LoL endpoint work is revisited.
- **Whether `eu.battle.net` is measuring the right thing for Warzone** — it's the Blizzard login layer, not Demonware's game backend. May only reflect login-service latency, not real match-server latency.
- **GCP address on port 1119** (`35.204.122.188`) seen during Warzone trace — same port as WoW's real game-data endpoint in `games.py`. Not investigated.
- **Real-time per-match server detection** — confirmed on both Warzone (Demonware) and Apex (AWS multi-region) that a single hardcoded endpoint can't represent "the server you'd actually play in" for titles with dynamic datacenter assignment. `trace_connections.py` proves the psutil approach works; turning it into a live in-app feature is the real fix. v3 scope.
- **World of Warcraft (`eu.actual.battle.net:1119`)** — DNS/WHOIS-checked Session 19 (Google Cloud, Netherlands), inconclusive without a live trace. Shipping unverified; retail free trial (Starter Edition) is the path for future verification.
- **Valorant** — audited Session 19, confirmed class 3 (unconnected UDP). Shipping endpoints unchanged as login/API latency proxy. Wireshark is the only path to real match server discovery.
- **CS2** — audited Session 19 via live `netstat`, confirmed class 3 via Valve SDR. Server IPs are intentionally hidden by design — no client-side tool can reach them. Shipping unchanged; existing "Steam servers" label was already honest.
- **Dota 2** — documented Session 19 by inference from CS2's SDR finding. Shipping unchanged. Lower evidence tier — worth a real trace if a Dota-2-playing tester becomes available.
- **League of Legends** — audited Session 19 via live `netstat` during active ARAM, confirmed class 3 (unconnected UDP, same Riot pattern as Valorant). Two-process architecture (`LeagueClient.exe` / `League of Legends.exe`). Shipping unchanged. Misleading `region_note` values for Valorant ("EU West") and LoL ("EUW") corrected same session — see resolved note in the LoL section.
- **Apex Legends `exe` alias check** — the alias list (`r5apex.exe` / `r5apex_dx12.exe`) was confirmed working live in Session 17, but no `migrate_game_endpoints()` exe entry was ever added at the time (the capability didn't exist yet). Worth confirming next session whether the dev's `games.json` already has the correct alias list or is relying on something else.
- **All 21 `DEFAULT_GAMES` entries are currently enabled** in the dev's `games.json` (changed Session 18 for testing, dev intends to leave as-is) — PingGuard is now monitoring all 21 endpoints every cycle. Worth keeping in mind if performance or Discord-report noise comes up.
- **Edit/remove game UI:** `update_game()` has no caller. Confirm `remove_game()` has a visible button wired to it before assuming removal works end to end.
- **psutil live-connection detection:** viable in principle (proven by `trace_connections.py`), but needs filtering logic before it can be a UI feature.
- **macOS / Linux:** pipeline builds both Windows and macOS as of Session 22 (`build-macos` job in `build.yml`, tag-triggered, real Release asset). Linux has no test build of any kind yet — genuinely still to do.
- **v2.3.0 data source:** psutil approach is the candidate to investigate first.
- **v3.0.0 elevation:** scapy vs. manual raw sockets — not decided.
- **Tray icon:** still shows generic blue circle instead of shield art. Dev's call to leave as low priority.
- **FFXIV `neolobby06.ffxiv.com` lead** — found during Session 19 desk audit, genuine named per-datacenter lobby server for Chaos/EU data center. Not yet WHOIS-confirmed or live-trace-verified. Stronger regional-split candidate than the current `frontier.ffxiv.com` global entry.
