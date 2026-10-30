#ifndef CONFIG_H
#define CONFIG_H

// ==================== HARDWARE CONFIGURATION ====================
#define NUM_PIXELS 50       // Total LED pixel blocks on strip
#define LED_DATA_PIN 13     // Renamed to avoid FastLED DATA_PIN template collision

// ==================== NETWORK CONFIGURATION ====================
const unsigned int LOCAL_UDP_PORT = 4210;
const char* const  MDNS_HOSTNAME  = "esp32-ambient";

#endif // CONFIG_H

