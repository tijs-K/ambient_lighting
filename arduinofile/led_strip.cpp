#include "led_strip.h"

static CRGB leds[NUM_PIXELS];
static const uint8_t HUE_STEP = 256 / NUM_PIXELS;

static bool          rainbowMode = false;
static uint8_t       rainbowHue  = 0;
static unsigned long lastRainbowUpdateMillis = 0;

void leds_setup() {
  // Initialize FastLED for WS2811 12V strips (GRB color order)
  FastLED.addLeds<WS2811, LED_DATA_PIN, GRB>(leds, NUM_PIXELS);
  FastLED.setBrightness(50); // Safe testing brightness
  leds_stop();
}

void leds_set_colors(const uint8_t* rgb_buffer, size_t num_pixels) {
  rainbowMode = false;
  // Bulk copy raw RGB bytes directly into FastLED buffer
  memcpy(leds, rgb_buffer, num_pixels * sizeof(CRGB));
  FastLED.show();
}

void leds_stop() {
  rainbowMode = false;
  fill_solid(leds, NUM_PIXELS, CRGB::Black);
  FastLED.show();
}

void leds_start_rainbow() {
  rainbowMode = true;
}

bool leds_is_rainbow_active() {
  return rainbowMode;
}

void leds_update_rainbow() {
  if (rainbowMode && millis() - lastRainbowUpdateMillis >= 20) {
    lastRainbowUpdateMillis = millis();
    for (int i = 0; i < NUM_PIXELS; i++) {
      leds[i] = CHSV(rainbowHue + (i * HUE_STEP), 255, 255);
    }
    FastLED.show();
    rainbowHue++;
  }
}

