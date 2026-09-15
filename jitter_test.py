"""
jitter_test.py - standalone diagnostic, not part of the shipped app.

Tests the Session 24 "Still To Do" item: does PingWorker.ping_all()'s
unthrottled one-thread-per-game design cause the ping jitter seen on
neolobby06.ffxiv.com:54994 (rock-stable 158-166ms isolated, but
159-818ms inside a real all-games cycle)?

Imports the REAL tcp_ping / check_riot_status / ping_game / DEFAULT_GAMES
from this project, so every test below exercises the actual functions
ping_all() calls - not a re-implementation of them. Run directly from
the project root:

    py jitter_test.py

Run 1 result (blocked design - all of A, then all of B, then C, then D):
A had the only bad outlier (one 485ms read, first call of the whole
script) while B/C/D - including B, the exact current unthrottled
behavior - were all tight (158-192ms). That's the opposite of what the
unthrottled-parallelism theory predicts, but a blocked design of only
10 cycles can't tell a real effect apart from "network was briefly
rough right when the script started" or "first network call this
process ever made was slow" - both confounds land squarely on A being
first, and 10 samples is thin for one spike either way.

Run 2 (this version) fixes the blocked-order and cold-start confounds
(warmup rounds discarded, A/B/C/D interleaved round-by-round) but is
still a short, fast-fire burst - it can't catch anything that only
shows up over a longer stretch of real time (a brief Wi-Fi/router hiccup
a few minutes in, ISP route changes, background Windows/Steam/Discord
traffic, etc.), and firing all four conditions back-to-back every ~1s
isn't how the real app behaves either (it pings once every
auto_check_interval, default 120s).

Run 3 (this version): same interleaved A/B/C/D design, but PACED - one
round every ROUND_INTERVAL_SECONDS instead of firing rounds back-to-back,
spread across a full RUN_MINUTES-minute window. This does two things a
short burst can't: (1) enough elapsed real time to catch anything that
only shows up intermittently rather than every single second, and (2) a
per-round table with wall-clock timestamps plus a spike co-occurrence
count at the end - if A spikes in the same round B/C/D also spike, that
points at a shared external cause (your network/ISP at that moment, not
this app); if only the unthrottled conditions spike while A stays clean,
that's real evidence for the parallelism theory.

Four conditions, each measuring the SAME FFXIV endpoint, one round of
all four running back-to-back before pacing to the next round:

  A) Isolated sequential  - one ping at a time, nothing else running.
     This is the Session 24 baseline (158-166ms) repeated for a fresh
     comparison point on today's network conditions.

  B) Unthrottled parallel - exact replica of ping_all(): a thread per
     DEFAULT_GAMES entry, all t.start()'d in a tight loop, no cap, no
     stagger. If jitter reappears here but not in A, that implicates
     the concurrency itself (network/OS contention from firing ~21
     sockets/HTTPS calls at once), not the endpoint.

  C) Candidate fix - bounded thread pool (max_workers=5) instead of
     unlimited threads.

  D) Candidate fix - same unlimited threads as B, but staggered
     t.start() calls (50ms apart) instead of firing them all at once.

C and D are two different shapes for "throttle it" - a hard concurrency
cap vs. spreading start times - run so the fix isn't assumed, only
whichever one (if either) actually tightens the readings gets proposed.

Every condition pings/status-checks all 21 DEFAULT_GAMES each round,
same as a real ping_all() call - this generates real traffic to the
same third-party game servers the app already contacts on every normal
2-minute cycle. Paced at one round every ROUND_INTERVAL_SECONDS (default
30s) across RUN_MINUTES (default 30), total volume works out to roughly
2 requests/second averaged over the run - lower rate than a person
actively refreshing a webpage, and far below anything that would look
like abuse to Riot/Steam/EA/etc, just spread over half an hour instead
of a few seconds.
"""
import concurrent.futures
import datetime
import statistics
import threading
import time

from ping_engine import tcp_ping, check_riot_status, ping_game
from games import DEFAULT_GAMES

TARGET_NAME = "Final Fantasy XIV"
TARGET_HOST = "neolobby06.ffxiv.com"
TARGET_PORT = 54994
WARMUP_ROUNDS = 3          # discarded, run back-to-back to warm DNS/sockets
RUN_MINUTES = 30           # total wall-clock time for the recorded phase
ROUND_INTERVAL_SECONDS = 30  # target spacing between the START of each round
SPIKE_THRESHOLD_MS = 250   # run 1's clean readings topped out at 192ms;
                           # the original in-app problem swung to 818ms -
                           # 250 sits well above normal noise, well below that
USER_REGION = "EU"

FFXIV_IDX = next(i for i, g in enumerate(DEFAULT_GAMES) if g["name"] == TARGET_NAME)


def ping_target():
    ms, success, _error = tcp_ping(TARGET_HOST, TARGET_PORT)
    return ms if success else None


def run_one_game(game, results, idx):
    """Same branching as PingWorker._ping_one(), minus the settings/
    game_manager side effects - we only need each game's thread to do
    the same real network work, and to record FFXIV's own result."""
    if idx == FFXIV_IDX:
        results[idx] = ping_target()
    elif game.get("status_platform"):
        check_riot_status(game, USER_REGION)
    else:
        ping_game(game)


def one_unthrottled_cycle():
    results = [None] * len(DEFAULT_GAMES)
    threads = []
    for idx, game in enumerate(DEFAULT_GAMES):
        t = threading.Thread(target=run_one_game, args=(game, results, idx), daemon=True)
        threads.append(t)
        t.start()
    for t in threads:
        t.join(timeout=10)
    return results[FFXIV_IDX]


def one_capped_cycle(max_workers=5):
    results = [None] * len(DEFAULT_GAMES)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = [ex.submit(run_one_game, game, results, idx)
                for idx, game in enumerate(DEFAULT_GAMES)]
        concurrent.futures.wait(futs, timeout=15)
    return results[FFXIV_IDX]


def one_staggered_cycle(stagger_s=0.05):
    results = [None] * len(DEFAULT_GAMES)
    threads = []
    for idx, game in enumerate(DEFAULT_GAMES):
        t = threading.Thread(target=run_one_game, args=(game, results, idx), daemon=True)
        threads.append(t)
        t.start()
        time.sleep(stagger_s)
    for t in threads:
        t.join(timeout=10)
    return results[FFXIV_IDX]


def summarize(label, values):
    clean = [v for v in values if v is not None]
    print(f"\n{label}")
    print(f"  raw: {values}")
    if len(clean) >= 2:
        print(f"  min={min(clean)} max={max(clean)} spread={max(clean) - min(clean)} "
              f"mean={statistics.mean(clean):.1f} stdev={statistics.stdev(clean):.1f}")
    elif clean:
        print(f"  single value: {clean[0]} (not enough successful pings for spread/stdev)")
    else:
        print("  no successful pings")


def run_one_round():
    """One interleaved A/B/C/D round. Returns (a, b, c, d)."""
    a_val = ping_target()
    time.sleep(0.1)
    b_val = one_unthrottled_cycle()
    time.sleep(0.1)
    c_val = one_capped_cycle()
    time.sleep(0.1)
    d_val = one_staggered_cycle()
    return a_val, b_val, c_val, d_val


def is_spike(ms):
    return ms is None or ms >= SPIKE_THRESHOLD_MS


if __name__ == "__main__":
    print(f"Target: {TARGET_HOST}:{TARGET_PORT} ({TARGET_NAME})")
    print(f"DEFAULT_GAMES count: {len(DEFAULT_GAMES)}  (FFXIV index: {FFXIV_IDX})")
    print(f"Warmup rounds (discarded): {WARMUP_ROUNDS}")
    print(f"Recorded phase: paced ~1 round / {ROUND_INTERVAL_SECONDS}s for "
          f"~{RUN_MINUTES} minutes  (spike threshold: {SPIKE_THRESHOLD_MS}ms)\n")
    print("Warming up (discarded, back-to-back, no pacing)...")

    for _ in range(WARMUP_ROUNDS):
        a_val, b_val, c_val, d_val = run_one_round()
        print(f"  warmup  A={a_val}  B={b_val}  C={c_val}  D={d_val}")
        time.sleep(0.3)

    print(f"\nRecording, paced. Sit tight for ~{RUN_MINUTES} minutes.\n")
    a_vals, b_vals, c_vals, d_vals = [], [], [], []
    spike_rows = []  # (round_num, {cond: bool spiked})

    print(f"{'round':>5}  {'time':>8}  {'A':>5}  {'B':>5}  {'C':>5}  {'D':>5}  spikes")
    run_start = time.monotonic()
    round_num = 0
    while time.monotonic() - run_start < RUN_MINUTES * 60:
        round_start = time.monotonic()
        a_val, b_val, c_val, d_val = run_one_round()
        round_num += 1

        a_vals.append(a_val)
        b_vals.append(b_val)
        c_vals.append(c_val)
        d_vals.append(d_val)

        flags = {"A": is_spike(a_val), "B": is_spike(b_val),
                 "C": is_spike(c_val), "D": is_spike(d_val)}
        spike_rows.append((round_num, flags))
        spike_str = "".join(cond for cond, hit in flags.items() if hit) or "-"
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"{round_num:>5}  {ts:>8}  {a_val!s:>5}  {b_val!s:>5}  "
              f"{c_val!s:>5}  {d_val!s:>5}  {spike_str}")

        elapsed_in_round = time.monotonic() - round_start
        time.sleep(max(0.0, ROUND_INTERVAL_SECONDS - elapsed_in_round))

    summarize("A) Isolated sequential (baseline)", a_vals)
    summarize("B) Unthrottled parallel - exact ping_all() replica", b_vals)
    summarize("C) Candidate fix - capped pool (max_workers=5)", c_vals)
    summarize("D) Candidate fix - staggered start (50ms between threads)", d_vals)

    print(f"\nSpike co-occurrence (>= {SPIKE_THRESHOLD_MS}ms or failed), "
          f"{round_num} rounds:")
    only = {"A": 0, "B": 0, "C": 0, "D": 0}
    multi = 0
    none_count = 0
    for _rn, flags in spike_rows:
        hits = [c for c, hit in flags.items() if hit]
        if len(hits) == 0:
            none_count += 1
        elif len(hits) == 1:
            only[hits[0]] += 1
        else:
            multi += 1
    print(f"  no spike in any condition: {none_count}")
    print(f"  spike in exactly one condition: A-only={only['A']} "
          f"B-only={only['B']} C-only={only['C']} D-only={only['D']}")
    print(f"  spike in 2+ conditions same round (shared external cause): {multi}")
    print("  -> if B/C/D-only counts are high and A-only is low: parallelism "
          "theory gains support.")
    print("  -> if A-only is high or 'multi' dominates: points at your "
          "network/ISP at that moment, not this app's threading.")

    print("\nDone. Paste this whole output back (including the full "
          "per-round table) for the root-cause read.")
