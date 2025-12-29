#!/usr/bin/python3
import pi_servo_hat
import time
import sys

if len(sys.argv) < 3:
  print("ERR: Not enough args. usage: test_servo1.py <servo_idx> <degrees>")
  exit(9)

# Initialize Constructor
servo_controller = pi_servo_hat.PiServoHat()

# Restart Servo Hat (in case Hat is frozen/locked)
#servo_controller.restart()

# Moves servo position to 0 degrees (1ms), Channel 0
print(f"Servo {sys.argv[1]} - at {sys.argv[2]} degrees")
servo_controller.move_servo_position(int(sys.argv[1]), int(sys.argv[2]))
