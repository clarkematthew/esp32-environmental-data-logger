#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_BME680.h"
#include "secrets/credentials.h"

#define SEALEVELPRESSURE_HPA (1013.25) // Adjust this to your local sea level pressure

Adafruit_BME680 bme(&Wire); // I2C interface

void connectToWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("WiFi connected. ESP32 IP: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  delay(2000); // Wait for sensor to stabilize
  Serial.begin(9600); // Start serial communication at 9600 baud

  connectToWiFi();

  if (!bme.begin()) {
    Serial.println("Could not find a valid BME680 sensor, check wiring!");
    while (1);
  }

  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
  }

  if (!bme.performReading()) {
    Serial.println("Failed to perform reading :(");
    return;
  }

  float temperatureF = ((bme.temperature) * (9.0 / 5.0)) + 32;
  float pressureHpa = bme.pressure / 100.0;
  float humidityPct = bme.humidity;
  float gasKohms = bme.gas_resistance / 1000.0;
  float altitudeFt = bme.readAltitude(SEALEVELPRESSURE_HPA) * 3.28084;

  String payload = "{";
  payload += "\"temperature_f\":" + String(temperatureF, 2) + ",";
  payload += "\"pressure_hpa\":" + String(pressureHpa, 2) + ",";
  payload += "\"humidity_pct\":" + String(humidityPct, 2) + ",";
  payload += "\"gas_kohms\":" + String(gasKohms, 2) + ",";
  payload += "\"altitude_ft\":" + String(altitudeFt, 2);
  payload += "}";

  HTTPClient http;
  http.begin(SERVER_URL);
  http.setTimeout(30000);
  http.addHeader("Content-Type", "application/json");

  Serial.print("Posting to ");
  Serial.println(SERVER_URL);
  Serial.print("Payload: ");
  Serial.println(payload);

  int httpResponseCode = http.POST(payload);
  if (httpResponseCode > 0) {
    Serial.print("Sent reading over WiFi. HTTP ");
    Serial.println(httpResponseCode);
  } else {
    Serial.print("WiFi send failed: ");
    Serial.println(http.errorToString(httpResponseCode));
  }

  http.end();
  delay(300000);
}
