//int x;
int pwm[6] = {0, 0, 0, 0, 0, 0};
const int pwmPins[6] = {3, 5, 6, 10, 11, 12};  // 11 is weaker than the others

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(1);
  for (int i = 0; i < 6; i++) {
    pinMode(pwmPins[i], OUTPUT);
  }
//  pinMode(6, OUTPUT);
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
  int power = (int)(0.4*255);
  analogWrite(pwmPins[5], power);
  delay(1);
}
