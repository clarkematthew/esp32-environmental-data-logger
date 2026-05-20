# ESP32 Environmental Data Logger

## Overview

This project uses an ESP32 and a BME680 sensor to track indoor environmental
conditions. The ESP32 reads temperature, pressure, humidity, gas resistance, and
estimated altitude, then sends the readings over WiFi to a Python server.

The Python code saves the current readings in `data/data.csv`, keeps older
daily summaries in `data/archive.csv`, and updates a dashboard image for an
e-paper display or local preview.

The goal of this project was to build a small end-to-end data logging system
that connects embedded hardware, networking, Python data handling, and a simple
display workflow.

## Hardware

- Inland ESP32 development board
- BME680 environmental sensor module
- Raspberry Pi or another computer to receive readings
- Optional Inky/e-paper display
- Breadboard, jumper wires, and USB power

## Wiring

The BME680 communicates with the ESP32 over I2C.

| BME680 pin | ESP32 pin |
| --- | --- |
| VCC | 3.3V |
| GND | GND |
| SDA | GPIO 21 |
| SCL | GPIO 22 |

## How It Works

1. The ESP32 connects to WiFi and starts the BME680 sensor.
2. Every five minutes, it reads the current sensor values.
3. The ESP32 sends a JSON payload to the Python server at `/sensor-data`.
4. `receiver/receive_data.py` checks the payload and appends the reading to `data/data.csv`.
5. When a new day starts, the previous day's readings are summarized into `data/archive.csv`.
6. `receiver/display_data.py` renders the newest readings into `data/display_preview.png` and updates the e-paper display when hardware is available.

## Project Files

- `platformio.ini` - PlatformIO configuration for building and uploading the ESP32 firmware.
- `src/main.cpp` - ESP32 firmware for reading the sensor and sending data over WiFi.
- `src/credentials.example.h` - Example WiFi and server configuration.
- `receiver/receive_data.py` - Python HTTP server that receives and stores sensor readings.
- `receiver/display_data.py` - Creates the dashboard image for preview or e-paper display.
- `receiver/requirements.txt` - Python dependencies for the receiver/display scripts.
- `receiver/receive_data.service` - Example systemd service file for running the receiver automatically.
- `receiver/install_receive_service.sh` - Installs and starts the receiver service.
- `data/data.csv` - Current active readings.
- `data/archive.csv` - Daily archived summaries.
- `data/display_preview.png` - Latest rendered dashboard preview.

## ESP32 Setup

Copy `src/credentials.example.h` to `src/secrets/credentials.h` and fill
in the WiFi name, WiFi password, and server URL:

```cpp
const char* WIFI_SSID = "your-wifi-name";
const char* WIFI_PASSWORD = "your-wifi-password";
const char* SERVER_URL = "http://your-server-ip:8000/sensor-data";
```

Open the repo in PlatformIO, then build and upload the firmware to your ESP32.
The firmware uses the Adafruit BME680 library and sends readings with the
Arduino `HTTPClient` library. Your real `src/secrets/credentials.h` is ignored
by Git so WiFi credentials are not published.

## Python Setup

Install the Python packages:

```bash
pip install -r receiver/requirements.txt
```

Run the receiver:

```bash
python3 receiver/receive_data.py
```

Render a dashboard preview without updating hardware:

```bash
python3 receiver/display_data.py --no-hardware
```

## Data Format

The ESP32 sends JSON like this:

```json
{
  "temperature_f": 72.45,
  "pressure_hpa": 1009.82,
  "humidity_pct": 42.10,
  "gas_kohms": 18.73,
  "altitude_ft": 112.52
}
```

The Python server adds the timestamp and stores the row in `data/data.csv`:

```csv
Time,Temperature (F),Pressure (hPa),Humidity (%),Gas (KOhms),Altitude (ft)
```

## What I Learned

- How to read environmental sensor data from a BME680 using an ESP32.
- How I2C wiring and sensor setup work on a microcontroller.
- How to send data from an ESP32 to another device over WiFi.
- How to receive JSON data with a small Python HTTP server.
- How to store live readings in CSV files for later analysis.
- How to summarize older readings so the active data file stays manageable.
- How to generate a simple dashboard image with Python.
- How to run a Python receiver automatically on a Raspberry Pi using systemd.

## Challenges

- Moving from serial output to WiFi-based data transfer.
- Deciding how often to collect readings without creating unnecessary data.
- Keeping the current data separate from older archived readings.
- Making the display update automatically when new data arrives.

## Next Steps

- Add trend charts to the dashboard.
- Make the server port and file paths easier to configure.
- Add tests for the daily archive behavior.
- Improve error handling if the ESP32 cannot reach the server.
