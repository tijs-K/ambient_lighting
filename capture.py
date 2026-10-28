"""
capture.py — screen capture loop, image processing, and latency measurement.
"""

import time
import numpy as np
import mss

import config
import state


def zone_colors_vectorized(sample_area: np.ndarray, num_zones: int) -> bytes:
    """
    Compute the average RGB color for each horizontal zone in one NumPy operation.

    Replaces a per-zone loop with a single reshape → mean.
    Returns raw bytes (num_zones × 3, RGB order) ready to send over UDP.
    """
    h, w, _ = sample_area.shape
    zone_w   = w // num_zones
    trimmed  = np.ascontiguousarray(sample_area[:, : zone_w * num_zones, :])
    zone_bgr = trimmed.reshape(h, num_zones, zone_w, 3).mean(axis=(0, 2)).astype(np.uint8)
    return zone_bgr[:, ::-1].tobytes()  # BGR → RGB


def capture_loop() -> None:
    """Main capture loop with precise per-stage latency profiling."""
    with mss.mss() as sct:
        monitor = sct.monitors[config.MONITOR_INDEX]

        # Pre-compute the capture region so we only pull what we need from the GPU
        if config.CAPTURE_MODE == "center":
            top_offset = monitor["top"] + (monitor["height"] - config.CENTER_BAND_HEIGHT) // 2
            grab_box = {
                "left": monitor["left"],
                "top": top_offset,
                "width": monitor["width"],
                "height": config.CENTER_BAND_HEIGHT,
            }
        else:
            grab_box = monitor

        while not state.stop.is_set():
            if not state.streaming.is_set():
                time.sleep(0.05)  # idle while a command holds the LEDs
                continue

            frame_start = time.monotonic()

            # 1. Screen Capture Stage — grabs only the target box directly from OS GDI
            t0 = time.perf_counter()
            sample_area = np.asarray(sct.grab(grab_box))[:, :, :3]
            t1 = time.perf_counter()
            capture_ms = (t1 - t0) * 1000.0

            # 2. Vectorized NumPy Compute Stage
            t2 = time.perf_counter()
            payload = zone_colors_vectorized(
                sample_area[:: config.SAMPLE_STEP, :: config.SAMPLE_STEP],
                config.NUM_ZONES,
            )
            t3 = time.perf_counter()
            compute_ms = (t3 - t2) * 1000.0

            # 3. UDP Network Send Stage
            t4 = time.perf_counter()
            state.sock.sendto(payload, (config.ESP32_IP, config.PORT))
            t5 = time.perf_counter()
            network_ms = (t5 - t4) * 1000.0

            # Measure total loop time & record telemetry
            elapsed = time.monotonic() - frame_start
            sleep_time = config.FRAME_INTERVAL - elapsed
            is_late = sleep_time < 0

            state.telemetry.record_frame(capture_ms, compute_ms, network_ms, is_late)

            if sleep_time > 0:
                time.sleep(sleep_time)
