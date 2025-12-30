#!/usr/bin/env python3

import os
import shutil
import time
import threading
from datetime import datetime

from flask import Flask, render_template_string, jsonify
import pi_servo_hat

# ============================================================
# Configuration
# ============================================================

WAIT_BETWEEN_FOLDING_CYCLES = 15
SLEEP_AFTER_CLOSED = 1
SLEEP_BETWEEN_FLAPS = 2

LOG_BASE = "/var/log/laundry_folder.log"

# ============================================================
# Paths
# ============================================================

FILE_REALPATH = os.path.realpath(__file__)
FOLDER_REALPATH = os.path.dirname(FILE_REALPATH)
WAV_PATH = os.path.join(FOLDER_REALPATH, "wav")

# ============================================================
# Global state
# ============================================================

MODE_AUTOMATIC = True
state_lock = threading.Lock()

# ============================================================
# Servo
# ============================================================

servo_controller = pi_servo_hat.PiServoHat()

# ============================================================
# Flask
# ============================================================

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>Laundry Folder</title>
  <style>
    body {
      margin: 0;
      background: #111;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      font-family: Arial, sans-serif;
      color: white;
    }

    #bigButton {
      width: 95vmin;
      height: 95vmin;
      border-radius: 50%;
      border: none;
      font-size: 3em;
      background: #555;
      color: #222;
    }

    #bigButton.enabled {
      background: red;
      color: white;
      cursor: pointer;
    }

    /* ===== Switch ===== */

    #modeSwitch {
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 150px;
      height: 48px;
      background: #333;
      border-radius: 24px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 12px;
      box-sizing: border-box;
      user-select: none;
    }

    #modeSwitch .label {
      font-size: 0.8em;
      color: #aaa;
      z-index: 2;
    }

    #modeSwitch .knob {
      position: absolute;
      top: 4px;
      left: 4px;
      width: 40px;
      height: 40px;
      background: #666;
      border-radius: 50%;
      transition: transform 0.25s ease, background 0.25s ease;
    }

    #modeSwitch.manual .knob {
      transform: translateX(102px);
      background: red;
    }

    #modeSwitch.manual .right {
      color: white;
    }

    #modeSwitch:not(.manual) .left {
      color: white;
    }
  </style>
</head>
<body>

<button id="bigButton" disabled>FOLD</button>

<div id="modeSwitch">
  <div class="knob"></div>
  <span class="label left">AUTO</span>
  <span class="label right">MANUAL</span>
</div>

<script>
async function updateState() {
  const r = await fetch("/state");
  const s = await r.json();

  const bigBtn = document.getElementById("bigButton");
  const sw = document.getElementById("modeSwitch");

  if (s.mode === "manual") {
    bigBtn.disabled = false;
    bigBtn.classList.add("enabled");
    sw.classList.add("manual");
  } else {
    bigBtn.disabled = true;
    bigBtn.classList.remove("enabled");
    sw.classList.remove("manual");
  }
}

document.getElementById("modeSwitch").onclick = async () => {
  await fetch("/toggle", { method: "POST" });
  updateState();
};

document.getElementById("bigButton").onclick = async () => {
  await fetch("/fold", { method: "POST" });
};

updateState();
</script>

</body>
</html>
"""

# ============================================================
# Helpers
# ============================================================

def log(message: str):
    ts = datetime.now().isoformat()
    line = f"[{ts}] {message}"
    print(line)
    with open(LOG_BASE, "a") as f:
        f.write(line + "\\n")


def rotate_logs():
    if os.path.exists(f"{LOG_BASE}.5"):
        os.remove(f"{LOG_BASE}.5")

    for i in range(4, 0, -1):
        src = f"{LOG_BASE}.{i}"
        dst = f"{LOG_BASE}.{i + 1}"
        if os.path.exists(src):
            shutil.move(src, dst)

    if os.path.exists(LOG_BASE):
        shutil.move(LOG_BASE, f"{LOG_BASE}.1")


def play_wav(filename: str):
    os.system(f"aplay '{filename}'")


def move_servo(channel: int, angle: int):
    log(f"Servo {channel} -> {angle}")
    servo_controller.move_servo_position(channel, angle)

# ============================================================
# Servo logic
# ============================================================

def initialize_servos():
    log("Initializing servos")

    servo_controller.restart()

    for i in range(3):
        move_servo(i, 75)

    time.sleep(2)

    open_position = {0: 155, 1: 0, 2: 0}
    for i in range(3):
        move_servo(i, open_position[i])
        time.sleep(1)

    log("Servo initialization completed")


def folding_cycle():
    log("Folding cycle started")

    move_servo(0, 0)
    time.sleep(SLEEP_AFTER_CLOSED)
    move_servo(0, 155)
    time.sleep(SLEEP_BETWEEN_FLAPS)

    move_servo(1, 155)
    time.sleep(SLEEP_AFTER_CLOSED)
    move_servo(1, 0)
    time.sleep(SLEEP_BETWEEN_FLAPS)

    move_servo(2, 155)
    time.sleep(SLEEP_AFTER_CLOSED)
    move_servo(2, 0)

    log("Folding cycle finished")

# ============================================================
# Background automatic loop
# ============================================================

def automatic_loop():
    while True:
        with state_lock:
            auto = MODE_AUTOMATIC

        if auto:
            log("Automatic mode: waiting before cycle")
            time.sleep(WAIT_BETWEEN_FOLDING_CYCLES)

            with state_lock:
                if MODE_AUTOMATIC:
                    play_wav(os.path.join(WAV_PATH, "prepare_laundry1.wav"))
                    folding_cycle()
        else:
            time.sleep(0.5)

# ============================================================
# Flask routes
# ============================================================

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)


@app.route("/state")
def state():
    with state_lock:
        return jsonify(mode="automatic" if MODE_AUTOMATIC else "manual")


@app.route("/toggle", methods=["POST"])
def toggle():
    global MODE_AUTOMATIC
    with state_lock:
        MODE_AUTOMATIC = not MODE_AUTOMATIC
        log(f"Mode changed to {'AUTOMATIC' if MODE_AUTOMATIC else 'MANUAL'}")
    return ("", 204)


@app.route("/fold", methods=["POST"])
def fold_once():
    with state_lock:
        if MODE_AUTOMATIC:
            return ("Disabled", 403)

    threading.Thread(target=folding_cycle, daemon=True).start()
    return ("", 204)

# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    rotate_logs()
    log("Service started NOW")

    initialize_servos()

    threading.Thread(target=automatic_loop, daemon=True).start()

    log("Web server started")
    app.run(host="0.0.0.0", port=80)
