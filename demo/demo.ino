//const int pwmPins[6] = {5, 6, 9, 10, 11};  // 11 is weaker than the others
//const int pwmPins[4] = {5, 11, 9, 6};  // bottom right, bottom left, top right, top left  // (old) top right, top left, bottom left, bottom right
const int pwmPins[4] = {5, 10, 11, 6};  // bottom right, bottom left, top right, top left  // (old) top right, top left, bottom left, bottom right
// pin 3, 5, and 6 wired to wrong pins, removed pin 3

int mode = 1;  // 1 = Directional, 2 = Adirectional, 3 = Cyclic, 4 = Off
int pin_to_actuate1 = 3;
int pin_to_actuate2 = 3;
int currPinIndex = 0;
int pwm = 0;
bool on = false;
long lastTime = 0;
long period = 1000;  // time between on/off cycles

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(1);
  for (int i = 0; i < 6; i++) {
    pinMode(pwmPins[i], OUTPUT);
  }
  lastTime = millis();
}

void loop() {
  if (Serial.available() >= 4) {
    //Reset pins
    for (int i = 0; i < 4; i++) {
      analogWrite(pwmPins[i], 0);
    }

    // Parse inputs
    mode = Serial.read();
    pin_to_actuate1 = Serial.read();
    pin_to_actuate2 = Serial.read();
    pwm = Serial.read();
    on = false;
    if (mode == 3) {
      currPinIndex = 0;
      analogWrite(pwmPins[currPinIndex], pwm);
    }
    lastTime = millis();
  }

  long currTime = millis();
  if (mode == 1) {
    if (on && (currTime > (lastTime + 1000))) {
      analogWrite(pin_to_actuate1, 0);
      analogWrite(pin_to_actuate2, 0);
      on = false;
      lastTime = currTime;
    } else if (!on && (currTime > (lastTime + 500))) {
      analogWrite(pin_to_actuate1, pwm);
      analogWrite(pin_to_actuate2, pwm);
      on = true;
      lastTime = currTime;
    }
  } else if (mode == 2) {
    if (on && (currTime > (lastTime + 1000))) {
      for (int i = 0; i < 4; i++) {
        analogWrite(pwmPins[i], 0);
      }
      on = false;
      lastTime = currTime;
    } else if (!on && (currTime > (lastTime + 500))) {
      for (int i = 0; i < 4; i++) {
        analogWrite(pwmPins[i], pwm);
      }
      on = true;
      lastTime = currTime;
    }
  } else if (mode == 3) {
    if (currPinIndex < 3) {  // for pins < 3, run 1s before switching
      if (currTime > (lastTime + 1000)) {
        analogWrite(pwmPins[currPinIndex], 0);
        currPinIndex += 1;
        analogWrite(pwmPins[currPinIndex], pwm);
        lastTime = currTime;
      }
    } else {
      if (currTime > (lastTime + 3000)) {
        analogWrite(pwmPins[currPinIndex], 0);
        currPinIndex = 0;
        analogWrite(pwmPins[currPinIndex], pwm);
        lastTime = currTime;
      }
    }
    Serial.println(currPinIndex);
  }

  delay(1);
}
