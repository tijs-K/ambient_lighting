import os

# Automatically load from local .env file if present (kept out of git)
_env_file = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_file):
    with open(_env_file) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

# ==================== ESP32 SETTINGS ====================
# Configured via .env file or environment variables
ESP32_IP  = os.getenv("ESP32_IP", "192.168.0.xxx")  # Override in local .env
PORT      = int(os.getenv("PORT", "4210"))
NUM_ZONES = int(os.getenv("NUM_ZONES", "50"))

# ==================== CAPTURE SETTINGS ====================
MONITOR_INDEX      = 3        # mss monitor index (1-based; 0 = all monitors combined)
CAPTURE_MODE       = "center" # "center" = 90% less GPU overhead; "full" = entire screen
CENTER_BAND_HEIGHT = 120      # Band height in pixels (1920x120 vs 1920x1080)
SAMPLE_STEP        = 8        # Spatial downsample factor
FRAME_RATE         = 10       # 10 FPS is smooth on a wall and drastically lowers GPU stalls
FRAME_INTERVAL     = 1 / FRAME_RATE
