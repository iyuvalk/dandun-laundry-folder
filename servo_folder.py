#!/usr/bin/python3
import pi_servo_hat
import time
import sys
from datetime import datetime, timezone


def log(log_msg):
  print(log_msg)
  with open("/var/log/laundry_folder.log", "a") as logfile:
    logfile.write(log_msg + "\n")

try:
  # Initialize Constructor
  servo_controller = pi_servo_hat.PiServoHat()

  servo_pos = [
    {"open": 0, "close": 90},
    {"open": 0, "close": 90},
    {"open": 0, "close": 90},
  ]
  sleep_after_flap_closed = 1
  sleep_between_servos = 7
  for i in range(3):
    for deg in [servo_pos[i]["open"], servo_pos[i]["close"], servo_pos[i]["open"]]:
      # Moves servo position to 0 degrees (1ms), Channel 0
      log(f"[{datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')}] Servo {i} - at {deg} degrees")
      servo_controller.move_servo_position(i, deg)
      if deg == servo_pos[i]["close"]:
        log(f"[{datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')}] Sleeping for {sleep_after_flap_closed} sec...")
        time.sleep(sleep_after_flap_closed)

    log(f"[{datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')}] Sleeping for {sleep_between_servos} sec before the next servo...")
except Exception as ex:
  log(f"[{datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')}] FAILED DUE TO EXCEPTION: {ex}")
