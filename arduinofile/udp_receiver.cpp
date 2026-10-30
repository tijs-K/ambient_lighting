#include "udp_receiver.h"
#include "led_strip.h"

static WiFiUDP       udp;
static uint8_t       packetBuffer[NUM_PIXELS * 3 + 1];
static unsigned long packetsReceived   = 0;
static unsigned long lastPacketMillis  = 0;
static int           lastPacketSize    = 0;

// Hardware FPS measurement
static unsigned long fpsCounter        = 0;
static unsigned long lastFpsCheckTime  = 0;
static float         currentFps        = 0.0;

void udp_setup() {
  udp.begin(LOCAL_UDP_PORT);
  Serial.printf("[UDP] Listener started on port %u\n", LOCAL_UDP_PORT);
}

void udp_loop() {
  int packetSize = udp.parsePacket();
  if (!packetSize) return;

  int len = udp.read(packetBuffer, sizeof(packetBuffer) - 1);
  if (len < 0) {
    Serial.println("[UDP] Failed to read packet.");
    return;
  }

  packetsReceived++;
  lastPacketMillis = millis();
  lastPacketSize   = len;

  // 1. Text commands
  if (len == 7 && memcmp(packetBuffer, "rainbow", 7) == 0) {
    leds_start_rainbow();
    Serial.println("[Command] Rainbow mode triggered.");
  } else if (len == 4 && memcmp(packetBuffer, "stop", 4) == 0) {
    leds_stop();
    Serial.println("[Command] LEDs stopped.");
  }
  // 2. Raw RGB Color Stream (NUM_PIXELS * 3 bytes)
  else if (len == NUM_PIXELS * 3) {
    // Calculate received hardware FPS
    fpsCounter++;
    unsigned long now = millis();
    if (now - lastFpsCheckTime >= 1000) {
      currentFps = (float)fpsCounter * 1000.0 / (now - lastFpsCheckTime);
      fpsCounter = 0;
      lastFpsCheckTime = now;
    }

    leds_set_colors(packetBuffer, NUM_PIXELS);
  } else {
    Serial.printf("[UDP] Unknown packet (%d bytes).\n", len);
  }
}

unsigned long udp_get_packets_received() { return packetsReceived; }
int           udp_get_last_packet_size()   { return lastPacketSize; }
float         udp_get_received_fps()      { return currentFps; }

unsigned long udp_get_last_packet_age_ms() {
  return (lastPacketMillis == 0) ? 0 : (millis() - lastPacketMillis);
}

