# 💡 Real-Time Ambient Lighting & IoT LED Controller

> **Status:** 🚧 **Work in Progress / Active Development**  
> A high-performance, low-latency ambient backlighting system syncing WS2811 addressable LEDs with PC monitor content in real time via an ESP32 and UDP networking.

---

## 📖 Overview

This project turns an **ESP32 microcontroller** and **WS2811 addressable LED strip** into a smart ambient display backlight. 

A multithreaded Python application running on your PC captures screen content, downsamples it using vectorized **NumPy** operations, and streams raw RGB color data over **UDP** directly to the ESP32. The ESP32 processes packets instantly, pushes colors to the physical strip using **FastLED**, and hosts an **Over-The-Air (OTA)** web dashboard for wireless firmware updates.

```
┌──────────────────┐    GDI Box Capture     ┌──────────────────────┐
│  Monitor Screen  │ ─────────────────────> │ Vectorized NumPy (PC)│
└──────────────────┘                        └──────────┬───────────┘
                                                       │  UDP Packet (150 bytes)
                                                       ▼
┌──────────────────┐    FastLED (memcpy)    ┌──────────────────────┐
│ WS2811 LED Strip │ <───────────────────── │    ESP32 Controller  │
└──────────────────┘                        └──────────────────────┘
```

---

## ✨ Features

* **⚡ Ultra-Low Latency Pipeline:** Frame compute takes `<1 ms` using single-pass NumPy array reshaping and color averaging—no per-pixel or per-zone Python loops.
* **🎮 Gaming Optimized:**
  * Runs at `IDLE` OS process priority so competitive games (e.g., *Valorant*) always get 100% CPU scheduling.
  * Direct GDI box capture (`"center"` band) reduces GPU PCIe readback overhead by **~90%** compared to full-screen captures.
* **📶 Wireless Over-The-Air (OTA) Updates:** Built-in web server powered by **ElegantOTA** allows flashing new firmware directly over Wi-Fi without needing a USB cable.
* **📊 Built-in Telemetry & Benchmarking:**
  * Live profiling of capture time, compute time, and network latency (`stats` / `fps`).
  * Direct hardware querying to verify ESP32 packet reception and ingest rate (`esp`).
  * CV / portfolio benchmark generator (`bench [seconds]`).
* **🎨 Standalone Modes:** Trigger independent animations (`rainbow`, `solid <r> <g> <b>`, `stop`) that run autonomously on the ESP32 chip without requiring PC streaming.

---

## 🗺️ Project Roadmap

- [x] Multi-zone vectorized screen color extraction (Python + NumPy).
- [x] Low-latency UDP streaming server & client.
- [x] FastLED embedded firmware with bulk memory copying (`memcpy`).
- [x] ElegantOTA wireless firmware flashing & zero-allocation status endpoint.
- [x] Interactive CLI with decorator-based command system.
- [x] Real-time latency & FPS telemetry.
- [ ] **📱 Companion Android App:** A mobile application (Flutter / Kotlin) to control power, solid colors, brightness, and animations over local Wi-Fi without needing the PC running.
- [ ] **Autonomous Hardware Wave/Scanner Effects:** Additional standalone C++ animations stored in ESP32 flash memory for zero-PC ambient lighting.
- [ ] **Auto-Discovery (mDNS / SSDP):** Automatically find the ESP32 on the local network without manually setting static IPs.

---

## 🛠️ Tech Stack & Hardware

### Hardware
* **Microcontroller:** ESP32 (NodeMCU / DevKit v1)
* **LED Strip:** WS2811 12V Addressable LED Strip (50 zones / 5 meters)
* **Power Supply:** 12V DC power brick with shared ground

### Software
* **Firmware:** C++, Arduino Core for ESP32, FastLED, WiFiUDP, WebServer, ElegantOTA
* **Host Application:** Python 3.10+, NumPy, `mss`, `psutil`

---

## 🚀 Getting Started

### 1. ESP32 Firmware Setup
1. Open [`arduinofile/arduinofile.ino`](arduinofile/arduinofile.ino) in Arduino IDE.
2. In the `arduinofile/` folder, copy `secrets.example.h` to `secrets.h`:
   ```bash
   cp arduinofile/secrets.example.h arduinofile/secrets.h
   ```
3. Open `secrets.h` and fill in your local Wi-Fi credentials:
   ```cpp
   #define WIFI_SSID "Your_WiFi_Network"
   #define WIFI_PASSWORD "Your_WiFi_Password"
   ```
   *(Note: `secrets.h` is ignored by git and will never be pushed to your repository).*
4. In Arduino IDE under **Tools**:
   * **Board:** `ESP32 Dev Module`
   * **Partition Scheme:** `Minimal SPIFFS (1.9MB APP with OTA/190KB SPIFFS)` *(required for OTA)*
5. Flash to the ESP32 via USB. Open the Serial Monitor (115200 baud) and note the assigned IP address.

### 2. Python Host Setup
1. Clone the repository and enter the directory:
   ```bash
   git clone https://github.com/your-username/ambient_lighting.git
   cd ambient_lighting
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Open [`config.py`](config.py) and update `ESP32_IP` with your device's IP:
   ```python
   ESP32_IP = "192.168.0.xxx"
   ```

### 3. Running the System
Start the screen capture and CLI:
```bash
python main.py
```

---

## 🎮 CLI Commands

While `main.py` is streaming, you can type commands directly into the terminal:

| Command | Description |
|---|---|
| `stream` | Resumes screen capture streaming to the LEDs |
| `pause` | Freezes the LEDs on their current colors |
| `solid <r> <g> <b>` | Sets all LEDs to a custom RGB color (e.g. `solid 255 0 0` for red) |
| `rainbow` | Triggers standalone autonomous rainbow animation |
| `stop` | Turns off all LEDs |
| `stats` / `fps` | Shows live framerate, microsecond latency breakdown, and CPU usage |
| `esp` | Fetches live hardware health, received packet counts, and ingest rate from ESP32 |
| `bench [sec]` | Runs a timed benchmark (e.g., `bench 10`) and prints a performance report |
| `quit` | Cleanly terminates the streamer |

---

## 🔒 Security & Privacy Notice

* **Wi-Fi Credentials:** All network passwords are kept strictly inside [`arduinofile/secrets.h`](arduinofile/secrets.example.h), which is excluded from version control via `.gitignore`.
* **Local LAN Communication:** UDP packets and HTTP status endpoints operate strictly within your local subnet without external cloud dependencies.

---

## 📄 License
This project is open-source under the MIT License.

