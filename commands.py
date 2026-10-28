"""
commands.py — command registry, telemetry displays, and LED commands.
"""

import time
import json
import urllib.request
import urllib.error

import config
import state

# ================================================================
#  REGISTRY
# ================================================================

COMMANDS: dict[str, tuple] = {}


def command(name: str, description: str, usage: str = ""):
    """Decorator that registers a function as a named LED command."""
    def decorator(fn):
        COMMANDS[name] = (fn, description, usage or name)
        return fn
    return decorator


def dispatch(raw: str) -> bool:
    """
    Parse and run one line of input.
    Returns False if the user wants to quit, True otherwise.
    """
    parts = raw.strip().split()
    if not parts:
        return True

    name = parts[0].lower()
    args = parts[1:]

    if name in ("quit", "exit", "q"):
        return False

    if name in COMMANDS:
        try:
            COMMANDS[name][0](args)
        except Exception as e:
            print(f"Error running '{name}': {e}")
    else:
        print(f"Unknown command: '{name}'. Type 'help' for a list.")

    return True


# ================================================================
#  TELEMETRY & PERFORMANCE COMMANDS
# ================================================================

@command("fps", "Display real-time FPS and latency breakdown", usage="fps")
def cmd_fps(args):
    """Alias for stats."""
    cmd_stats(args)


@command("stats", "Display pipeline latency, FPS, and CPU metrics", usage="stats")
def cmd_stats(args):
    data = state.telemetry.snapshot()
    target_interval = config.FRAME_INTERVAL * 1000.0  # in ms
    headroom_ms = max(0.0, target_interval - data["total_ms"])

    print("\n" + "=" * 50)
    print("      REAL-TIME PIPELINE TELEMETRY")
    print("=" * 50)
    print(f"  Streaming Status:      {'ACTIVE' if state.streaming.is_set() else 'PAUSED'}")
    print(f"  Streaming Framerate:   {data['fps']:.1f} FPS (Target: {config.FRAME_RATE} FPS)")
    print(f"  Total Frames Sent:     {data['total_frames']:,}")
    print(f"  Late / Dropped Frames: {data['late_frames']}")
    print("-" * 50)
    print("  LATENCY BREAKDOWN (per frame average):")
    print(f"    • Screen Grab (mss):    {data['capture_ms']:6.2f} ms")
    print(f"    • Vectorized Compute:   {data['compute_ms']:6.2f} ms")
    print(f"    • Network Send (UDP):   {data['network_ms']:6.2f} ms")
    print(f"    • Total Active Latency: {data['total_ms']:6.2f} ms")
    print(f"    • Available Headroom:   {headroom_ms:6.2f} ms ({headroom_ms / target_interval * 100:.1f}% idle)")
    print("-" * 50)
    print("  SYSTEM IMPACT:")
    print(f"    • Process CPU Usage:    {data['cpu_percent']:.1f}%")
    print(f"    • Memory Footprint:     {data['memory_mb']:.1f} MB")
    print("=" * 50 + "\n")


@command("esp", "Query hardware metrics directly from ESP32", usage="esp")
def cmd_esp(args):
    url = f"http://{config.ESP32_IP}/status"
    print(f"Querying ESP32 at {url}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AmbientTelemetry/1.0"})
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        print("\n" + "=" * 50)
        print("          ESP32 HARDWARE TELEMETRY")
        print("=" * 50)
        print(f"  Wi-Fi Connected:       {data.get('wifi_connected')}")
        print(f"  ESP32 IP:              {data.get('ip')}")
        print(f"  UDP Port:              {data.get('udp_port')}")
        print(f"  Total Packets RX:      {data.get('udp_packets_received', 0):,}")
        if "received_fps" in data:
            print(f"  Hardware Ingest FPS:   {data.get('received_fps'):.1f} FPS")
        print(f"  Last Packet Payload:   {data.get('last_udp_packet_bytes')} bytes")
        print(f"  Last Packet Age:       {data.get('last_packet_age_ms')} ms")
        print("=" * 50 + "\n")
    except urllib.error.URLError as e:
        print(f"Could not reach ESP32 HTTP server: {e.reason}")
    except Exception as e:
        print(f"Error querying ESP32: {e}")


@command("bench", "Run a timed benchmark and output a CV report", usage="bench [seconds]")
def cmd_bench(args):
    duration = int(args[0]) if args and args[0].isdigit() else 5
    if not state.streaming.is_set():
        print("Starting stream for benchmark...")
        state.streaming.set()

    print(f"\n[Benchmark] Profiling pipeline for {duration} seconds...")
    start_frames = state.telemetry.total_frames
    t_start = time.monotonic()
    time.sleep(duration)
    t_end = time.monotonic()
    data = state.telemetry.snapshot()

    frames_measured = data["total_frames"] - start_frames
    actual_fps = frames_measured / (t_end - t_start)

    print("\n" + "#" * 54)
    print("         BENCHMARK REPORT (FOR CV / PORTFOLIO)")
    print("#" * 54)
    print(f"  Test Duration:         {t_end - t_start:.2f} s")
    print(f"  Frames Streamed:       {frames_measured}")
    print(f"  Sustained Framerate:   {actual_fps:.2f} FPS (Target: {config.FRAME_RATE} FPS)")
    print(f"  Average Active Time:   {data['total_ms']:.2f} ms / frame")
    print(f"    - Screen Capture:    {data['capture_ms']:.2f} ms")
    print(f"    - Vectorized NumPy:  {data['compute_ms']:.2f} ms")
    print(f"    - UDP Network Send:  {data['network_ms']:.2f} ms")
    print(f"  Host CPU Overhead:     {data['cpu_percent']:.1f}% of 1 core")
    print(f"  Host RAM Usage:        {data['memory_mb']:.1f} MB")
    print("#" * 54 + "\n")


# ================================================================
#  BUILT-IN LED CONTROL COMMANDS
# ================================================================

@command("stream", "Resume screen capture to LEDs")
def cmd_stream(args):
    state.streaming.set()
    print("Screen capture streaming resumed.")


@command("pause", "Freeze LEDs on their current color")
def cmd_pause(args):
    state.streaming.clear()
    print("Streaming paused. Type 'stream' to resume.")


@command("stop", "Turn off all LEDs and pause streaming")
def cmd_stop(args):
    state.streaming.clear()
    state.sock.sendto(b"stop", (config.ESP32_IP, config.PORT))
    print("LEDs off. Type 'stream' to resume capture.")


@command("rainbow", "Start the rainbow animation on the LEDs")
def cmd_rainbow(args):
    state.streaming.clear()
    state.sock.sendto(b"rainbow", (config.ESP32_IP, config.PORT))
    print("Rainbow mode started. Type 'stream' to resume capture.")


@command("solid", "Set all LEDs to one solid color", usage="solid <r> <g> <b>")
def cmd_solid(args):
    if len(args) != 3:
        print("Usage: solid <r> <g> <b>   (each value 0–255)")
        return
    try:
        r, g, b = int(args[0]), int(args[1]), int(args[2])
        if not all(0 <= v <= 255 for v in (r, g, b)):
            raise ValueError
    except ValueError:
        print("Error: r, g, b must be integers between 0 and 255.")
        return
    state.streaming.clear()
    state.sock.sendto(bytes([r, g, b] * config.NUM_ZONES), (config.ESP32_IP, config.PORT))
    print(f"Solid color → RGB({r}, {g}, {b}). Type 'stream' to resume capture.")


@command("help", "List all available commands")
def cmd_help(args):
    status = "streaming" if state.streaming.is_set() else "paused"
    print()
    print(f"  Status: {status}  |  ESP32 → {config.ESP32_IP}:{config.PORT}")
    print()
    print(f"  {'COMMAND':<30} DESCRIPTION")
    print(f"  {'-'*30} {'-'*32}")
    for name, (fn, desc, usage) in sorted(COMMANDS.items()):
        print(f"  {usage:<30} {desc}")
    print(f"  {'quit':<30} Stop everything and exit")
    print()
