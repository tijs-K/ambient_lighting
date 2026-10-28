# ==================== ESP32 SETTINGS ====================
ESP32_IP  = "192.168.0.166"  # Your ESP32's IP (shown in Serial Monitor on boot)
PORT      = 4210             # UDP port — must match localPort in arduinofile.ino
NUM_ZONES = 50               # LED pixel blocks — must match NUM_PIXELS in arduinofile.ino

# ==================== CAPTURE SETTINGS ====================
MONITOR_INDEX      = 3      # mss monitor index (1-based; 0 = all monitors combined)
CAPTURE_MODE       = "center" # "center" = 90% less GPU overhead; "full" = entire screen
CENTER_BAND_HEIGHT = 120    # Band height in pixels (1920x120 vs 1920x1080)
SAMPLE_STEP        = 8      # Spatial downsample factor
FRAME_RATE         = 10     # 10 FPS is smooth on a wall and drastically lowers GPU stalls
FRAME_INTERVAL     = 1 / FRAME_RATE
