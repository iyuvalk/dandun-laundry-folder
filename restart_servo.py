#!/usr/bin/python3
import pi_servo_hat
import time


# Initialize Constructor
servo_controller = pi_servo_hat.PiServoHat()

# Restart Servo Hat (in case Hat is frozen/locked)
servo_controller.restart()
servo_controller.move_servo_position(0, 75)
servo_controller.move_servo_position(1, 75)
servo_controller.move_servo_position(2, 75)

time.sleep(2)
open_position = {
  0: 155,
  1: 0,
  2: 0
}
for i in range(3):
  servo_controller.move_servo_position(i, open_position[i])
  time.sleep(1)
