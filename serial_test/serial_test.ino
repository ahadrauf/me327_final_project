//int x;
int pwm[6] = {0, 0, 0, 0, 0, 0};

void setup() {
 Serial.begin(115200);
 Serial.setTimeout(1);
}

void loop() {
// while (!Serial.available());
// x = Serial.readString().toInt();
// Serial.print(x + 1);
  while (Serial.available() >= 6) {
    for (int i = 0; i < 6; i ++) {
      pwm[i] = Serial.read();
      Serial.print(pwm[i] + 1);
    }
  }
}
