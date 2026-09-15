"""
dns_isolation_test.py - standalone diagnostic, not part of the shipped app.

Follow-up to jitter_test.py's 30-minute paced run. That run disconfirmed
the Session 24 "unthrottled parallel pinging" theory: B (the exact
ping_all() replica) was tight (1 spike/60 rounds, stdev 24.9), while A
(isolated, sequential, ZERO concurrency) carried nearly all the jitter
(14 spikes/60, stdev 82.9) - including an 11-round stretch (22:22:30-
22:32:30) alternating spike/clean on an almost exact 60-second period.
B/C/D, pinging the SAME endpoint moments later in the SAME round, were
clean every one of those times (multi-condition co-occurrence: 0/60) -
so whatever slows A down clears again within about a second, before
B/C/D's turn in the same round.

Leading theory now: DNS resolution, not threading. tcp_ping() passes a
hostname straight to socket.connect_ex(), which resolves it fresh via
getaddrinfo() on every single call - Python does not cache this itself.
Windows' own DNS Client service does cache resolutions system-wide, but
only until the record's TTL expires; whichever caller happens to make
the first call after expiry pays for a real upstream lookup, and every
caller after it (within the same round, milliseconds to ~1s later)
rides the now-warm cache. A always runs first in jitter_test.py's
rounds - so A would be the one that keeps drawing the short straw.

This test isolates that directly, three ways, interleaved every round:

  DNS  - time ONLY socket.getaddrinfo(TARGET_HOST, ...) - nothing else.
  HOST - the real tcp_ping() against the hostname (resolution + connect,
         same as jitter_test.py's condition A).
  IP   - tcp_ping() against the already-resolved numeric IP - bypasses
         hostname resolution entirely every call.

If DNS and HOST spike together while IP stays flat, that confirms DNS
resolution as the mechanism - not PingGuard's threading, not general
network congestion (IP is just as exposed to the network as HOST, only
the resolution step differs).

Run directly from the project root:

    py dns_isolation_test.py

While this runs, optionally open a second terminal and leave
`ping -t neolobby06.ffxiv.com` running to eyeball whether plain ICMP
shows the same pattern - a free extra data point this script doesn't
need to capture itself.
"""
import datetime
import socket
import statistics
import time

from ping_engine import tcp_ping

TARGET_HOST = "neolobby06.ffxiv.com"
TARGET_PORT = 54994
WARMUP_ROUNDS = 3
RUN_MINUTES = 25
ROUND_INTERVAL_SECONDS = 20   # denser than jitter_test.py's 30s - the
                              # suspected ~60s period needs at least a
                              # couple of samples per cycle to resolve
SPIKE_THRESHOLD_MS = 250


def resolve_only():
    start = time.perf_counter()
    try:
        socket.getaddrinfo(TARGET_HOST, TARGET_PORT, socket.AF_INET, socket.SOCK_STREAM)
        return round((time.perf_counter() - start) * 1000)
    except Exception:
        return None


def ping_host():
    ms, success, _err = tcp_ping(TARGET_HOST, TARGET_PORT)
    return ms if success else None


def ping_ip(ip):
    ms, success, _err = tcp_ping(ip, TARGET_PORT)
    return ms if success else None


def is_spike(ms):
    return ms is None or ms >= SPIKE_THRESHOLD_MS


def summarize(label, values):
    clean = [v for v in values if v is not None]
    print(f"\n{label}")
    print(f"  raw: {values}")
    if len(clean) >= 2:
        print(f"  min={min(clean)} max={max(clean)} spread={max(clean) - min(clean)} "
              f"mean={statistics.mean(clean):.1f} stdev={statistics.stdev(clean):.1f}")
    elif clean:
        print(f"  single value: {clean[0]}")
    else:
        print("  no successful reads")


if __name__ == "__main__":
    print(f"Resolving {TARGET_HOST} once to get a control IP...")
    try:
        resolved_ip = socket.gethostbyname(TARGET_HOST)
    except Exception as e:
        print(f"Could not resolve {TARGET_HOST}: {e}")
        raise SystemExit(1)
    print(f"Control IP: {resolved_ip}\n")

    print(f"Warmup rounds (discarded): {WARMUP_ROUNDS}")
    print(f"Recorded phase: paced ~1 round / {ROUND_INTERVAL_SECONDS}s for "
          f"~{RUN_MINUTES} minutes  (spike threshold: {SPIKE_THRESHOLD_MS}ms)\n")

    for _ in range(WARMUP_ROUNDS):
        d, h, i = resolve_only(), ping_host(), ping_ip(resolved_ip)
        print(f"  warmup  DNS={d}  HOST={h}  IP={i}")
        time.sleep(0.5)

    print(f"\nRecording, paced. Sit tight for ~{RUN_MINUTES} minutes.\n")
    dns_vals, host_vals, ip_vals = [], [], []
    print(f"{'round':>5}  {'time':>8}  {'DNS':>5}  {'HOST':>5}  {'IP':>5}  spikes")

    run_start = time.monotonic()
    round_num = 0
    while time.monotonic() - run_start < RUN_MINUTES * 60:
        round_start = time.monotonic()
        d = resolve_only()
        time.sleep(0.1)
        h = ping_host()
        time.sleep(0.1)
        i = ping_ip(resolved_ip)
        round_num += 1

        dns_vals.append(d)
        host_vals.append(h)
        ip_vals.append(i)

        flags = []
        if is_spike(d):
            flags.append("DNS")
        if is_spike(h):
            flags.append("HOST")
        if is_spike(i):
            flags.append("IP")
        spike_str = "+".join(flags) or "-"
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"{round_num:>5}  {ts:>8}  {d!s:>5}  {h!s:>5}  {i!s:>5}  {spike_str}")

        elapsed = time.monotonic() - round_start
        time.sleep(max(0.0, ROUND_INTERVAL_SECONDS - elapsed))

    summarize("DNS  - getaddrinfo() alone", dns_vals)
    summarize("HOST - tcp_ping() via hostname (resolution + connect)", host_vals)
    summarize("IP   - tcp_ping() via resolved IP (no resolution)", ip_vals)

    print("\nCo-occurrence check:")
    dns_and_host = sum(1 for d, h in zip(dns_vals, host_vals) if is_spike(d) and is_spike(h))
    host_spike_ip_clean = sum(1 for h, i in zip(host_vals, ip_vals) if is_spike(h) and not is_spike(i))
    ip_spike_count = sum(1 for i in ip_vals if is_spike(i))
    print(f"  rounds where DNS and HOST both spiked together: {dns_and_host}")
    print(f"  rounds where HOST spiked but IP stayed clean: {host_spike_ip_clean}")
    print(f"  total IP spikes: {ip_spike_count}")
    print("  -> DNS+HOST spiking together, IP staying clean: confirms DNS "
          "resolution as the mechanism.")
    print("  -> IP spiking too (or as often as HOST): points at the network "
          "path itself, not resolution - DNS theory falsified.")

    print("\nDone. Paste this whole output back for the read.")
