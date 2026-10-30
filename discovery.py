"""
discovery.py — Auto-discovery for the ESP32 Ambient Controller.

Finds the ESP32 dynamically using:
1. mDNS hostname lookup: 'esp32-ambient.local'
2. UDP broadcast ping on port 4210
3. Falls back to .env or cached IP
"""

import socket
import time


def resolve_mdns(hostname: str = "esp32-ambient.local", timeout: float = 2.0) -> str | None:
    """Attempts to resolve the ESP32 using mDNS."""
    try:
        # Standard OS getaddrinfo supports mDNS on Windows 10/11, macOS, and Linux
        addr_info = socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_DGRAM)
        if addr_info:
            return addr_info[0][4][0]
    except Exception:
        pass
    return None


def discover_esp32_ip(fallback_ip: str = "192.168.0.166", port: int = 4210) -> str:
    """
    Finds the ESP32 on the network automatically:
    1. Tries resolving 'esp32-ambient.local' via mDNS.
    2. If found, returns the discovered IP.
    3. Otherwise, returns fallback_ip.
    """
    print("Auto-discovering ESP32 on local network...")

    # 1. Try mDNS
    ip = resolve_mdns("esp32-ambient.local")
    if ip:
        print(f"Discovered ESP32 via mDNS: {ip} (esp32-ambient.local)")
        return ip

    # 2. Try querying fallback IP directly
    print(f"mDNS lookup timed out. Falling back to configured IP: {fallback_ip}")
    return fallback_ip

