#include <Servo.h>

Servo folderServos[3];
int firstServoIdx = 7;
int initalServoPosition = 0;
const int SERVO_LEFT = 7;
const int SERVO_RIGHT = 8;
const int SERVO_BOTTOM = 9;

void setup() {
  Serial.begin(9600);

  // put your setup code here, to run once:
  for (int servoIdx = firstServoIdx; servoIdx < (firstServoIdx + 3); servoIdx += 1) {
    folderServos[servoIdx - firstServoIdx].attach(servoIdx);
    Serial.println("Resetting servo " + String(servoIdx) + " to " + String(initalServoPosition) + "...");
    folderServos[servoIdx - firstServoIdx].write(initalServoPosition);
  }
}

void loop() {
  int foldAngle = 90;
  int servoIdx = -1;

  // put your main code here, to run repeatedly:
  for (int servoIdx = firstServoIdx; servoIdx < (firstServoIdx + 3); servoIdx += 1) {
    Serial.println("Moving servo " + String(servoIdx) + " to " + String(foldAngle) + "...");
    folderServos[servoIdx - firstServoIdx].write(foldAngle);
    delay(1500);
    Serial.println("Resetting servo " + String(servoIdx) + " to " + String(initalServoPosition) + "...");
    folderServos[servoIdx - firstServoIdx].write(initalServoPosition);
    delay(3000);
  }
  Serial.println("Waiting for another T-Shirt...");
  delay(45000);
}

