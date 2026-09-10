#include <Arduino.h>
#include <OneWire.h>
#include <DallasTemperature.h>

constexpr uint8_t TEMP_PIN = 8;

OneWire oneWire(TEMP_PIN);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("DS18B20_MINIMAL_TEST");

  pinMode(TEMP_PIN, INPUT_PULLUP);

  sensors.begin();

  const uint8_t count = sensors.getDeviceCount();

  Serial.printf("DEVICE_COUNT=%u\n", count);

  if (count > 0) {
    DeviceAddress address;

    if (sensors.getAddress(address, 0)) {
      Serial.print("DEVICE_ADDRESS=");

      for (uint8_t i = 0; i < 8; i++) {
        if (address[i] < 0x10) {
          Serial.print('0');
        }

        Serial.print(address[i], HEX);
      }

      Serial.println();
    }
  }

  sensors.requestTemperatures();

  const float temperature =
      sensors.getTempCByIndex(0);

  Serial.printf(
      "TEMPERATURE=%.2f\n",
      temperature
  );
}

void loop() {
  delay(1000);
}