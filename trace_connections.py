"""
trace_connections.py - Quick diagnostic tool to find what server(s) a
running game is actually talking to right now.

NOT part of the PingGuard app itself. This is a throwaway research
script - same "verify it actually works before trusting it" discipline
used for the AWS endpoint check during the region-separation work.

HOW TO USE:
1. Launch the real game and get into an actual match (not just the
   main menu - menus often only talk to login/store servers, not the
   real game server).
2. Open a terminal in this folder and run, for example:
     python trace_connections.py cod.exe
   (use whatever the real .exe name is - check Task Manager if unsure)
3. It prints every remote address/port that process currently has open.
   Run it 2-3 times over a minute or so, since connections can take a
   moment to establish after a match starts.
4. The real game server is usually the connection that's NOT on port
   443 (443 is almost always login/store/CDN traffic, not gameplay) and
   shows steady repeated activity rather than a single one-off hit.
5. Once you have a candidate IP, note it down - we'll verify where it's
   actually hosted (and that it isn't another CDN/anycast address like
   the Cloudflare one already caught for Warzone) before it goes
   anywhere near games.py.
"""
import sys
import psutil


def find_connections(process_name):
    process_name = process_name.lower()
    found_any = False

    for proc in psutil.process_iter(["name", "pid"]):
        try:
            if proc.info["name"] and proc.info["name"].lower() == process_name:
                found_any = True
                print(f"\nProcess: {proc.info['name']} (PID {proc.info['pid']})")

                # psutil renamed Process.connections() to net_connections()
                # in some versions - try the new name first, fall back to
                # the old one so this works regardless of installed version.
                try:
                    connections = proc.net_connections(kind="inet")
                except AttributeError:
                    connections = proc.connections(kind="inet")

                if not connections:
                    print("  No active connections yet - get into a live match and try again.")

                for conn in connections:
                    if conn.raddr:
                        print(f"  -> {conn.raddr.ip}:{conn.raddr.port}  (status: {conn.status})")

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            print("  Could not read this process's connections (permission denied).")
            print("  Try running the terminal as Administrator and trying again.")

    if not found_any:
        print(f"No running process named '{process_name}' found. Is the game actually open?")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python trace_connections.py <process_name.exe>")
        sys.exit(1)
    find_connections(sys.argv[1])