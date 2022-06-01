//int x;
//int pwm[6] = {0, 0, 0, 0, 0, 0};
const int pwmPins[6] = {5, 6, 9, 10, 11};  // 11 is weaker than the others
// pin 3, 5, and 6 wired to wrong pins, removed pin 3

int pin_to_actuate = 5;
int pwm = 0;
bool on = false;
bool actuate = false;
long lastTime = 0;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(1);
  for (int i = 0; i < 6; i++) {
    pinMode(pwmPins[i], OUTPUT);
  }
//  pinMode(6, OUTPUT);
  lastTime = millis();
}

void loop() {
// while (!Serial.available());
// x = Serial.readString().toInt();
// Serial.print(x + 1);
//  while (Serial.available() >= 6) {
//    for (int i = 0; i < 6; i++) {
//      pwm[i] = Serial.read();
////      Serial.print(pwm[i] + 1);
//      analogWrite(
//    }
//  }
//  if (Serial.available() >= 2) {
//    analogWrite(pin_to_actuate, 0);
//    pin_to_actuate = Serial.read();
//    pwm = Serial.read();
//    if (pin_to_actuate == 0) {
//      actuate = false;
//    } else {
//      actuate = true;
//    }
//  }

  if (millis() > lastTime + 1000) {
    if (on) {
      analogWrite(pin_to_actuate, 0);
      on = false;
    } else {
      analogWrite(pin_to_actuate, pwm);
      on = true;
    }
  }
  
//  int power = (int)(0.8*255);
////  const int pins[4] = {9, 5, 4, 1};
//  const int pins[4] = {5, 9, 11, 6};
//  for (int i = 0; i < 4; i++) {
//    for (int j = 0; j < 4; j++) {
//      if (i == j) {
//        analogWrite(pins[i], power);
//      } else {
//        analogWrite(pins[j], 0);
//      }
//    }
//    delay(1000);
//  }
//  analogWrite(pwmPins[0], power);
//  analogWrite(pwmPins[5], 0);
//  delay(1000);
//  analogWrite(pwmPins[1], power);
//  analogWrite(pwmPins[4], 0);
//  delay(1000);
}
