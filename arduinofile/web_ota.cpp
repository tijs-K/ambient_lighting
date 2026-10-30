#include "web_ota.h"
#include <WebServer.h>
#include <WiFi.h>
#include <ElegantOTA.h>
#include "config.h"
#include "udp_receiver.h"

static WebServer server(80);
static unsigned long ota_progress_millis = 0;

void web_ota_setup() {
  // Root Dashboard
  server.on("/", HTTP_GET, []() {
    server.send(200, "text/html",
      "<!doctype html><html><head><meta name='viewport' content='width=device-width'>"
      "<meta http-equiv='refresh' content='3'><title>ESP32 LED Status</title></head><body>"
      "<h1>ESP32 Ambient Lighting Controller</h1>"
      "<p><a href='/status'>Hardware Telemetry (JSON)</a></p>"
      "<p><a href='/update'>OTA Wireless Firmware Update</a></p></body></html>");
  });

  // Zero-allocation stack buffer JSON endpoint
  server.on("/status", HTTP_GET, []() {
    char buf[256];
    snprintf(buf, sizeof(buf),
      "{\"wifi_connected\":%s,\"ip\":\"%s\",\"udp_port\":%u"
      ",\"udp_packets_received\":%lu,\"received_fps\":%.1f"
      ",\"last_udp_packet_bytes\":%d,\"last_packet_age_ms\":%lu}",
      WiFi.status() == WL_CONNECTED ? "true" : "false",
      WiFi.localIP().toString().c_str(),
      LOCAL_UDP_PORT,
      udp_get_packets_received(),
      udp_get_received_fps(),
      udp_get_last_packet_size(),
      udp_get_last_packet_age_ms()
    );
    server.send(200, "application/json", buf);
  });

  // ElegantOTA setup
  ElegantOTA.begin(&server);

  ElegantOTA.onStart([]() {
    Serial.println("[OTA] Update started!");
  });

  ElegantOTA.onProgress([](size_t current, size_t final) {
    if (millis() - ota_progress_millis > 1000) {
      ota_progress_millis = millis();
      if (final > 0) {
        Serial.printf("[OTA] Progress: %u%%\n", (current * 100) / final);
      }
    }
  });

  ElegantOTA.onEnd([](bool success) {
    Serial.println(success ? "[OTA] Update succeeded!" : "[OTA] Update failed!");
  });

  server.begin();
  Serial.println("[HTTP] OTA Web Server started on port 80.");
}

void web_ota_loop() {
  server.handleClient();
  ElegantOTA.loop();
}

