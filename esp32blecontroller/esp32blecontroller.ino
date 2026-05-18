#include <BleGamepad.h>

/*
  ESP32 Sega-style BLE controller

  Wiring:
  - Each button connects its GPIO pin to GND when pressed.
  - Internal pull-up resistors are enabled in setup().

  Required Arduino library:
  - lemmingDev BLE HID library
*/

#define DEVICE_NAME "BLE Controller"
#define DEVICE_MANUFACTURER "Muhammad Usama"

const uint8_t DPAD_UP = 13;
const uint8_t DPAD_DOWN = 12;
const uint8_t DPAD_LEFT = 14;
const uint8_t DPAD_RIGHT = 5;

const uint8_t BUTTON_TRIANGLE = 15;
const uint8_t BUTTON_CIRCLE = 4;
const uint8_t BUTTON_CROSS = 22;
const uint8_t BUTTON_SQUARE = 23;

const uint8_t BUTTON_L1 = 32;
const uint8_t BUTTON_L2 = 33;
const uint8_t BUTTON_R1 = 26;
const uint8_t BUTTON_R2 = 27;

const uint8_t BUTTON_L3 = 18;
const uint8_t BUTTON_R3 = 19;
const uint8_t BUTTON_START = 25;
const uint8_t BUTTON_SELECT = 21;

struct ButtonMap {
  uint8_t pin;
  uint8_t hidButton;
};

ButtonMap buttons[] = {
  {BUTTON_TRIANGLE, 1},
  {BUTTON_CIRCLE, 2},
  {BUTTON_CROSS, 3},
  {BUTTON_SQUARE, 4},
  {BUTTON_L1, 5},
  {BUTTON_L2, 6},
  {BUTTON_R1, 7},
  {BUTTON_R2, 8},
  {BUTTON_L3, 9},
  {BUTTON_R3, 10},
  {BUTTON_SELECT, 11},
  {BUTTON_START, 12},
};

const uint8_t dpadPins[] = {
  DPAD_UP,
  DPAD_DOWN,
  DPAD_LEFT,
  DPAD_RIGHT,
};

BleGamepad bleController(DEVICE_NAME, DEVICE_MANUFACTURER, 100);

bool isPressed(uint8_t pin) {
  return digitalRead(pin) == LOW;
}

signed char readHat() {
  bool up = isPressed(DPAD_UP);
  bool down = isPressed(DPAD_DOWN);
  bool left = isPressed(DPAD_LEFT);
  bool right = isPressed(DPAD_RIGHT);

  if (up && right && !down && !left) return HAT_UP_RIGHT;
  if (down && right && !up && !left) return HAT_DOWN_RIGHT;
  if (down && left && !up && !right) return HAT_DOWN_LEFT;
  if (up && left && !down && !right) return HAT_UP_LEFT;
  if (up && !down) return HAT_UP;
  if (right && !left) return HAT_RIGHT;
  if (down && !up) return HAT_DOWN;
  if (left && !right) return HAT_LEFT;

  return HAT_CENTERED;
}

void setupPins() {
  for (uint8_t i = 0; i < sizeof(dpadPins) / sizeof(dpadPins[0]); i++) {
    pinMode(dpadPins[i], INPUT_PULLUP);
  }

  for (uint8_t i = 0; i < sizeof(buttons) / sizeof(buttons[0]); i++) {
    pinMode(buttons[i].pin, INPUT_PULLUP);
  }
}

void setup() {
  Serial.begin(115200);
  setupPins();
  bleController.begin();
}

void loop() {
  if (!bleController.isConnected()) {
    delay(100);
    return;
  }

  bleController.setHat1(readHat());

  for (uint8_t i = 0; i < sizeof(buttons) / sizeof(buttons[0]); i++) {
    if (isPressed(buttons[i].pin)) {
      bleController.press(buttons[i].hidButton);
    } else {
      bleController.release(buttons[i].hidButton);
    }
  }

  delay(8);
}
