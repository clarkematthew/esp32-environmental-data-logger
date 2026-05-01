#include <Wire.h>
#include <SPI.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_BME680.h"


#define SEALEVELPRESSURE_HPA (1013.25) // Adjust this to your local sea level pressure

Adafruit_BME680 bme(&Wire); // I2C interface

const char* WIFI_SSID = "ClaSecureAccess";
const char* WIFI_PASSWORD = "WeLoveToParty";
const char* SERVER_URL = "192.168.0.221:8080/sensor-data";

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
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
  }

  // Perform a reading and check for success
  if (! bme.performReading()) {
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
  http.addHeader("Content-Type", "application/json");
  int httpResponseCode = http.POST(payload);
  if (httpResponseCode > 0) {
    Serial.print("Sent reading over WiFi. HTTP ");
    Serial.println(httpResponseCode);
  } else {
    Serial.print("WiFi send failed: ");
    Serial.println(http.errorToString(httpResponseCode));
  }

  http.end();
  delay(10000);
 }
