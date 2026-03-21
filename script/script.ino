#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_BME680.h"



#define SEALEVELPRESSURE_HPA (1013.25) // Adjust this to your local sea level pressure

Adafruit_BME680 bme(&Wire); // I2C interface

void setup() {
  delay(2000); // Wait for sensor to stabilize
  Serial.begin(9600); // Start serial communication at 9600 baud
  while (!Serial); // Wait for serial port to be available
  
  // Return error message if sensor is not found
  if (!bme.begin()) {
    Serial.println("Could not find a valid BME680 sensor, check wiring!");
    while (1);
  }

  
  bme.setTemperatureOversampling(BME680_OS_8X); // 8x oversampling for temperature
  bme.setHumidityOversampling(BME680_OS_2X); // 2x oversampling for humidity
  bme.setPressureOversampling(BME680_OS_4X); // 4x oversampling for pressure
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3); // IIR filter size 3
  bme.setGasHeater(320, 150); // Sets the gas heater to 320°C for 150 ms

 

}

void loop() {
  // Perform a reading and check for success
  if (! bme.performReading()) {
    Serial.println("Failed to perform reading :(");
    return;
  }

  // Temperature in Fahrenheit
  Serial.print(((bme.temperature) * (9.0/5.0)) + 32);
  Serial.print(",");

  // Pressure in hPa
  Serial.print(bme.pressure / 100.0);
  Serial.print(",");

  // Humidity in percentage
  Serial.print(bme.humidity);
  Serial.print(",");

  // Gas resistance in kOhms
  Serial.print(bme.gas_resistance / 1000.0);
  Serial.print(",");

  // Altitude in Feet
  Serial.print(bme.readAltitude(SEALEVELPRESSURE_HPA) * 3.28084);

  Serial.println();
delay(10000);
}