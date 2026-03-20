# esp32-environmental-data-logger
## Overview
This project uses an ESP32 and a BME680 sensor to measure temperature, humidity, pressure, and gas resistance. The system logs data at regular intervals and outputs it for analysis. The goal is to build a simple environmental monitoring setup and expand it into a standalone display using a Raspberry Pi and e-ink screen.

## Goals
- Learn how to interface sensors with a microcontroller
- Understand environmental data (especially gas resistance behavior)
- Build a reliable logging system
- Expand into a multi-day display system

## Hardware
- ESP32 development board
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

## Software Approach
The ESP32 runs a loop that reads sensor values using a BME680 library. Data is printed via serial output and logged into a CSV file on a connected computer.

## Sample Data
[Insert Picture Here]

## Key Learnings
- Basic sensor integration using I2C
- Differences between 3.3V and 5V systems
- How gas resistance changes with air quality/flow
- Challenges with continuous data logging

## Challenges
- Initial wiring and soldering setup
- Understanding gas sensor readings
- Managing logging frequency without slowing performance

## Next Steps
- Add Raspberry Pi for standalone operation
- Display multi-day data on an e-ink screen
- Improve data visualization
