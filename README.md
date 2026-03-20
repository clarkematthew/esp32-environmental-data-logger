# esp32-environmental-data-logger
## Overview
This project uses an ESP32 and a BME680 sensor to measure temperature, humidity, pressure, and gas resistance. The system logs data at regular intervals and outputs it for analysis. The goal is to build a simple environmental monitoring setup and expand it into a standalone display using a Raspberry Pi and e-ink screen.

## Final Output
[Insert Picture Here]

## Goals
- Learn how to interface sensors with a microcontroller
- Understand environmental data (especially gas resistance behavior)
- Build a reliable logging system
- Expand into a multi-day display system

## Hardware
- Inland ESP32 development board
- BME680 sensor module
- Breadboard and jumper wires
- USB power

## System Architecture
The ESP32 communicates with the BME680 over I2C. Sensor readings are taken at fixed intervals and sent over serial output. The data is captured and stored for later analysis.

## Wiring
- VCC → 3.3V (ESP32)
- GND → GND
- SDA → GPIO 21
- SCL → GPIO 22
[Insert Picture Here]

## Software Approach
The ESP32 runs a continuous loop that reads sensor values from the BME680 at fixed intervals. The data is formatted and sent over serial output.

A Python script reads the serial stream in real time, parses the incoming data, and stores it in a CSV file for later analysis.

## Data Pipeline
Sensor data flows from the ESP32 to a connected computer via serial communication. A Python script captures this stream, structures the data, and logs it to a CSV file.

This creates a simple end-to-end pipeline from data collection → processing → storage, which can be extended into visualization or dashboarding.

## Sample Data
[Insert Picture Here]


## Key Learnings
- Writing embedded code with continuous loops for real-time data collection
- Reading and parsing serial data using Python
- Building a basic data pipeline from hardware to storage
- Understanding I2C communication between microcontroller and sensor
- Observing how gas resistance changes with environmental conditions
- Managing logging frequency and performance tradeoffs
- 
## Challenges
- Initial wiring and soldering setup
- Understanding gas sensor readings
- Managing logging frequency without slowing performance

## Next Steps
- Add Raspberry Pi for standalone operation
- Display multi-day data on an e-ink screen
- Improve data visualization
