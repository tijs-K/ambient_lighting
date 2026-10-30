#include <Arduino.h>
#include "config.h"
#include "network_mgr.h"
#include "led_strip.h"
#include "udp_receiver.h"
#include "web_ota.h"

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n=== ESP32 Ambient Lighting Booting ===");

  // 1. Initialize LED strip
  leds_setup();

  // 2. Connect Wi-Fi and start mDNS
  network_setup();

  // 3. Start UDP packet listener
  udp_setup();

  // 4. Start HTTP WebServer & ElegantOTA
  web_ota_setup();

  Serial.println("=== System Ready ===");
}

void loop() {
  // 1. Ensure Wi-Fi stays connected
  network_keep_alive();

  // 2. Handle HTTP clients & OTA firmware flashes
  web_ota_loop();

  // 3. Process incoming UDP commands or color frames
  udp_loop();

  // 4. Handle standalone animations (e.g. rainbow)
  leds_update_rainbow();
}
