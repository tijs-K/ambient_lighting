#ifndef UDP_RECEIVER_H
#define UDP_RECEIVER_H

#include <Arduino.h>
#include <WiFiUdp.h>
#include "config.h"

void udp_setup();
void udp_loop();

// Telemetry getters for /status JSON
unsigned long udp_get_packets_received();
int           udp_get_last_packet_size();
unsigned long udp_get_last_packet_age_ms();
float         udp_get_received_fps();

#endif // UDP_RECEIVER_H

