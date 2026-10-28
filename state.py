"""
state.py — shared objects and live telemetry used across capture, commands, and main.
"""

import socket
import threading
import time
import os
import psutil

# Single UDP socket shared by the capture thread and all commands
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set   → capture thread sends frames to the ESP32
# Clear → capture is paused (a command has taken over the LEDs)
streaming = threading.Event()
streaming.set()

# Set to signal the capture thread to exit cleanly
stop = threading.Event()


class Telemetry:
    """Thread-safe telemetry tracker for screen capture, processing, and hardware metrics."""
    def __init__(self):
        self.lock = threading.Lock()
        self.process = psutil.Process(os.getpid())
        # Prime psutil cpu_percent
        self.process.cpu_percent()

        # Latency breakdown (exponential moving averages in ms)
        self.capture_ms = 0.0
        self.compute_ms = 0.0
        self.network_ms = 0.0
        self.total_ms = 0.0

        # Frame counters & rates
        self.total_frames = 0
        self.late_frames = 0
        self.fps = 0.0
        self._window_frames = 0
        self._window_start = time.monotonic()

    def record_frame(self, cap_ms: float, comp_ms: float, net_ms: float, is_late: bool):
        now = time.monotonic()
        with self.lock:
            self.total_frames += 1
            if is_late:
                self.late_frames += 1

            # Exponential moving average (alpha=0.1) for smooth latency readings
            alpha = 0.1
            self.capture_ms = (1 - alpha) * self.capture_ms + alpha * cap_ms
            self.compute_ms = (1 - alpha) * self.compute_ms + alpha * comp_ms
            self.network_ms = (1 - alpha) * self.network_ms + alpha * net_ms
            self.total_ms   = self.capture_ms + self.compute_ms + self.network_ms

            # 1-second rolling FPS calculation
            self._window_frames += 1
            window_elapsed = now - self._window_start
            if window_elapsed >= 1.0:
                self.fps = self._window_frames / window_elapsed
                self._window_frames = 0
                self._window_start = now

    def snapshot(self) -> dict:
        """Return a snapshot of current telemetry data."""
        with self.lock:
            mem_mb = self.process.memory_info().rss / (1024 * 1024)
            cpu = self.process.cpu_percent()
            return {
                "fps": self.fps,
                "capture_ms": self.capture_ms,
                "compute_ms": self.compute_ms,
                "network_ms": self.network_ms,
                "total_ms": self.total_ms,
                "total_frames": self.total_frames,
                "late_frames": self.late_frames,
                "cpu_percent": cpu,
                "memory_mb": mem_mb,
            }


telemetry = Telemetry()
