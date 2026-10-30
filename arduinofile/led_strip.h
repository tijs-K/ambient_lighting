#ifndef LED_STRIP_H
#define LED_STRIP_H

#include "config.h"
#include <FastLED.h>

// Initialize FastLED hardware
void leds_setup();

// Update colors from raw RGB buffer received over UDP
void leds_set_colors(const uint8_t* rgb_buffer, size_t num_pixels);

// Turn off all LEDs
void leds_stop();

// Trigger and update standalone rainbow animation
void leds_start_rainbow();
void leds_update_rainbow();
bool leds_is_rainbow_active();

#endif // LED_STRIP_H

