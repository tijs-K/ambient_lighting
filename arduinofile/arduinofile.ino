#include <WiFi.h>
#include <WiFiUdp.h>
#include <WebServer.h>
#include <ElegantOTA.h>
#include <FastLED.h>
#include "secrets.h"

// ==================== CONFIGURATION ====================
const char* ssid     = WIFI_SSID;
const char* password = WIFI_PASSWORD;

// LED Strip Configuration for 12V WS2811 (30 LEDs/m, 5m strip grouped into 50 blocks)
#define NUM_PIXELS 50
#define DATA_PIN   13

// Precomputed hue step for rainbow animation (compile-time constant)
static const uint8_t HUE_STEP = 256 / NUM_PIXELS;

CRGB leds[NUM_PIXELS];

// Networking & UDP
WiFiUDP udp;
const unsigned int localPort = 4210;
// uint8_t matches actual usage; +1 leaves room for a text-command null terminator
uint8_t packetBuffer[NUM_PIXELS * 3 + 1];
unsigned long udpPacketsReceived  = 0;
unsigned long lastUdpPacketMillis = 0;
int           lastUdpPacketSize   = 0;
unsigned long fpsPacketCount      = 0;
unsigned long lastFpsCheckMillis  = 0;
float         espReceivedFps      = 0.0;
bool          rainbowMode         = false;
uint8_t       rainbowHue          = 0;
unsigned long lastRainbowUpdateMillis = 0;

// Standard Web Server on port 80 (built into ESP32 core)
WebServer server(80);
unsigned long ota_progress_millis = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Initialize FastLED for WS2811 12V strips
  FastLED.addLeds<WS2811, DATA_PIN, GRB>(leds, NUM_PIXELS);
  FastLED.setBrightness(50);

  // Connect to Wi-Fi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected! ESP32 IP Address:");
  Serial.println(WiFi.localIP());

  // Start UDP Listener
  udp.begin(localPort);
  Serial.printf("UDP listener started on port %u\n", localPort);

  // --- OTA Web Server Setup ---
  server.on("/", HTTP_GET, []() {
    server.send(200, "text/html",
      "<!doctype html><html><head><meta name='viewport' content='width=device-width'>"
      "<meta http-equiv='refresh' content='3'><title>ESP32 LED Status</title></head><body>"
      "<h1>ESP32 LED Controller</h1><p><a href='/status'>UDP status (JSON)</a></p>"
      "<p><a href='/update'>OTA firmware update</a></p></body></html>");
  });

  // Zero-allocation JSON status using snprintf into a stack buffer
  server.on("/status", HTTP_GET, []() {
    char age[16];
    if (lastUdpPacketMillis == 0) {
      strcpy(age, "null");
    } else {
      snprintf(age, sizeof(age), "%lu", millis() - lastUdpPacketMillis);
    }

    char buf[256];
    snprintf(buf, sizeof(buf),
      "{\"wifi_connected\":%s,\"ip\":\"%s\",\"udp_port\":%u"
      ",\"udp_packets_received\":%lu,\"received_fps\":%.1f"
      ",\"last_udp_packet_bytes\":%d,\"last_packet_age_ms\":%s}",
      WiFi.status() == WL_CONNECTED ? "true" : "false",
      WiFi.localIP().toString().c_str(),
      localPort,
      udpPacketsReceived,
      espReceivedFps,
      lastUdpPacketSize,
      age
    );
    server.send(200, "application/json", buf);
  });

  ElegantOTA.begin(&server);

  ElegantOTA.onStart([]() {
    Serial.println("OTA update started!");
  });

  ElegantOTA.onProgress([](size_t current, size_t final) {
    if (millis() - ota_progress_millis > 1000) {
      ota_progress_millis = millis();
      if (final > 0) {
        Serial.printf("OTA Progress: %u%%\n", (current * 100) / final);
      }
    }
  });

  ElegantOTA.onEnd([](bool success) {
    Serial.println(success ? "OTA update finished successfully!" : "OTA update failed!");
  });

  server.begin();
  Serial.println("HTTP OTA server started.");
}

void loop() {
  // WiFi watchdog – reconnect automatically if connection drops
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi lost, reconnecting...");
    WiFi.reconnect();
    delay(500);
    return; // skip UDP and LED work until connected
  }

  // Handle standard web clients and OTA background tasks
  server.handleClient();
  ElegantOTA.loop();

  // Handle incoming UDP commands or LED color packets
  int packetSize = udp.parsePacket();
  if (packetSize) {
    int len = udp.read(packetBuffer, sizeof(packetBuffer) - 1);
    udpPacketsReceived++;
    lastUdpPacketMillis = millis();
    lastUdpPacketSize   = len; // use len (actual bytes read) for consistency

    if (len < 0) {
      Serial.println("Failed to read UDP packet.");
    } else if (len == 7 && memcmp(packetBuffer, "rainbow", 7) == 0) {
      rainbowMode = true;
      Serial.println("Rainbow mode started.");
    } else if (len == 4 && memcmp(packetBuffer, "stop", 4) == 0) {
      rainbowMode = false;
      fill_solid(leds, NUM_PIXELS, CRGB::Black);
      FastLED.show();
      Serial.println("LEDs stopped.");
    } else if (len == NUM_PIXELS * 3) {
      // Calculate hardware received FPS
      fpsPacketCount++;
      unsigned long now = millis();
      if (now - lastFpsCheckMillis >= 1000) {
        espReceivedFps = (float)fpsPacketCount * 1000.0 / (now - lastFpsCheckMillis);
        fpsPacketCount = 0;
        lastFpsCheckMillis = now;
      }

      // CRGB is a plain {r, g, b} struct; Python sends RGB so a single bulk
      // copy is correct. FastLED outputs GRB to the strip internally.
      rainbowMode = false;
      memcpy(leds, packetBuffer, NUM_PIXELS * 3);
      FastLED.show();
    } else {
      Serial.printf("Ignoring unknown UDP packet (%d bytes).\n", len);
    }
  }

  // Animate without blocking so Wi-Fi and the web server stay responsive
  if (rainbowMode && millis() - lastRainbowUpdateMillis >= 20) {
    lastRainbowUpdateMillis = millis();
    for (int i = 0; i < NUM_PIXELS; i++) {
      // HUE_STEP is a compile-time constant; avoids division in the hot loop
      leds[i] = CHSV(rainbowHue + (i * HUE_STEP), 255, 255);
    }
    FastLED.show();
    rainbowHue++;
  }
}
