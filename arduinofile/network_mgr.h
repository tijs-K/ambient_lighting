#ifndef NETWORK_MGR_H
#define NETWORK_MGR_H

#include <Arduino.h>
#include <WiFi.h>
#include <ESPmDNS.h>
#include "secrets.h"
#include "config.h"

// Connects to Wi-Fi and starts mDNS
void network_setup();

// Keeps Wi-Fi alive automatically in the background
void network_keep_alive();

#endif // NETWORK_MGR_H

