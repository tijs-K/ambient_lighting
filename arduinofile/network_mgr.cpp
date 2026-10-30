#include "network_mgr.h"

void network_setup() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n[Wi-Fi] Connected! ESP32 IP Address:");
  Serial.println(WiFi.localIP());

  // Start mDNS Responder (allows discovery as esp32-ambient.local)
  if (MDNS.begin(MDNS_HOSTNAME)) {
    Serial.printf("[mDNS] Responder started: http://%s.local\n", MDNS_HOSTNAME);
  } else {
    Serial.println("[mDNS] Error setting up responder!");
  }
}

void network_keep_alive() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[Wi-Fi] Connection lost! Reconnecting...");
    WiFi.reconnect();
    delay(500);
  }
}

