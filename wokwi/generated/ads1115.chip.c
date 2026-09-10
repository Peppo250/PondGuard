#include "wokwi-api.h"
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define REG_CONVERSION 0x00
#define REG_CONFIG     0x01
#define REG_LO_THRESH  0x02
#define REG_HI_THRESH  0x03

typedef struct {
  i2c_dev_t i2c;
  pin_t ain[4];
  pin_t alert;
  uint8_t pointer;
  uint8_t write_index;
  uint8_t read_index;
  uint16_t regs[4];
} chip_state_t;

static float fs_voltage(uint16_t config) {
  switch ((config >> 9) & 0x07) {
    case 0: return 6.144f;
    case 1: return 4.096f;
    case 2: return 2.048f;
    case 3: return 1.024f;
    case 4: return 0.512f;
    default: return 0.256f;
  }
}

static int16_t voltage_to_code(float voltage, float fs) {
  if (voltage > fs) voltage = fs;
  if (voltage < -fs) voltage = -fs;
  float scaled = voltage / fs * 32767.0f;
  if (scaled > 32767.0f) scaled = 32767.0f;
  if (scaled < -32768.0f) scaled = -32768.0f;
  return (int16_t)lroundf(scaled);
}

static float read_input(chip_state_t *chip, int index) {
  return pin_adc_read(chip->ain[index]);
}

static float selected_voltage(chip_state_t *chip, uint16_t config) {
  uint8_t mux = (config >> 12) & 0x07;
  switch (mux) {
    case 4: return read_input(chip, 0);
    case 5: return read_input(chip, 1);
    case 6: return read_input(chip, 2);
    case 7: return read_input(chip, 3);
    case 0: return read_input(chip, 0) - read_input(chip, 1);
    case 1: return read_input(chip, 0) - read_input(chip, 3);
    case 2: return read_input(chip, 1) - read_input(chip, 3);
    case 3: return read_input(chip, 2) - read_input(chip, 3);
    default: return 0.0f;
  }
}

static void perform_conversion(chip_state_t *chip) {
  uint16_t config = chip->regs[REG_CONFIG];
  float fs = fs_voltage(config);
  float volts = selected_voltage(chip, config);
  int16_t code = voltage_to_code(volts, fs);
  chip->regs[REG_CONVERSION] = (uint16_t)code;
  // Single-shot conversion is modeled as completing immediately. This preserves
  // the ADS1115 register contract while keeping Wokwi simulation responsive.
  chip->regs[REG_CONFIG] |= 0x8000u; // OS = conversion complete.
  pin_write(chip->alert, HIGH);
}

static bool on_i2c_connect(void *user_data, uint32_t address, bool read) {
  chip_state_t *chip = (chip_state_t *)user_data;
  (void)address;
  chip->read_index = 0;
  chip->write_index = 0;
  return true;
}

static uint8_t on_i2c_read(void *user_data) {
  chip_state_t *chip = (chip_state_t *)user_data;
  uint16_t value = chip->regs[chip->pointer & 0x03];
  uint8_t byte = (chip->read_index == 0) ? (uint8_t)(value >> 8) : (uint8_t)(value & 0xff);
  chip->read_index++;
  if (chip->read_index >= 2) chip->read_index = 0;
  return byte;
}

static bool on_i2c_write(void *user_data, uint8_t data) {
  chip_state_t *chip = (chip_state_t *)user_data;
  if (chip->write_index == 0) {
    chip->pointer = data & 0x03;
    chip->write_index = 1;
    return true;
  }

  static uint8_t msb = 0;
  if (chip->write_index == 1) {
    msb = data;
    chip->write_index = 2;
    return true;
  }

  chip->regs[chip->pointer & 0x03] = ((uint16_t)msb << 8) | data;
  chip->write_index = 0;

  if ((chip->pointer & 0x03) == REG_CONFIG) {
    uint16_t config = chip->regs[REG_CONFIG];
    bool single_shot = ((config >> 8) & 0x01u) != 0;
    bool start = (config & 0x8000u) != 0;
    if (single_shot && start) {
      chip->regs[REG_CONFIG] &= ~0x8000u;
      pin_write(chip->alert, LOW);
      perform_conversion(chip);
    }
  }
  return true;
}

static void on_i2c_disconnect(void *user_data) {
  chip_state_t *chip = (chip_state_t *)user_data;
  chip->write_index = 0;
  chip->read_index = 0;
}

void chip_init() {
  chip_state_t *chip = (chip_state_t *)malloc(sizeof(chip_state_t));
  if (!chip) return;

  chip->ain[0] = pin_init("A0", ANALOG);
  chip->ain[1] = pin_init("A1", ANALOG);
  chip->ain[2] = pin_init("A2", ANALOG);
  chip->ain[3] = pin_init("A3", ANALOG);
  chip->alert = pin_init("ALRT", OUTPUT);
  chip->pointer = REG_CONVERSION;
  chip->write_index = 0;
  chip->read_index = 0;
  for (int i = 0; i < 4; ++i) chip->regs[i] = 0;
  chip->regs[REG_CONFIG] = 0x8583;
  pin_write(chip->alert, HIGH);

  const i2c_config_t i2c = {
    .address = 0x48,
    .scl = pin_init("SCL", INPUT_PULLUP),
    .sda = pin_init("SDA", INPUT_PULLUP),
    .connect = on_i2c_connect,
    .read = on_i2c_read,
    .write = on_i2c_write,
    .disconnect = on_i2c_disconnect,
    .user_data = chip,
  };
  chip->i2c = i2c_init(&i2c);
}
