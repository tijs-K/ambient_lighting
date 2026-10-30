import os
from pathlib import Path
from discovery import discover_esp32_ip

# Load .env directly relative to this file's folder if present
_env_file = Path(__file__).resolve().parent / ".env"
if _env_file.is_file():
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ[_k.strip()] = _v.strip().strip('"').strip("'")

# ==================== ESP32 SETTINGS ====================
# Default port and zones
PORT      = int(os.environ.get("PORT", "4210"))
NUM_ZONES = int(os.environ.get("NUM_ZONES", "50"))

# Preferred/fallback IP from .env or default
_configured_ip = os.environ.get("ESP32_IP", "192.168.0.166").strip()

# Automatically discover ESP32 via mDNS (esp32-ambient.local), falling back to _configured_ip
ESP32_IP = discover_esp32_ip(fallback_ip=_configured_ip, port=PORT)

# ==================== CAPTURE SETTINGS ====================
MONITOR_INDEX      = 2       # mss monitor index (1-based; 0 = all monitors combined)
CAPTURE_MODE       = "center" # "center" = 90% less GPU overhead; "full" = entire screen
CENTER_BAND_HEIGHT = 120      # Band height in pixels (1920x120 vs 1920x1080)
SAMPLE_STEP        = 8        # Spatial downsample factor
FRAME_RATE         = 10       # 10 FPS is smooth on a wall and drastically lowers GPU stalls
FRAME_INTERVAL     = 1 / FRAME_RATE
