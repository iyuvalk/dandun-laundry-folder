#!/bin/bash
FILE="${0}"
FILE_REALPATH=$(realpath "${FILE}")
FOLDER_REALPATH=$(dirname "${FILE_REALPATH}")
WAV_PATH="${FOLDER_REALPATH}/wav"
WAIT_BETWEEN_FOLDING_CYCLES=15
SLEEP_AFTER_CLOSED=1
SLEEP_BETWEEN_FLAPS=2

[[ -f /var/log/laundry_folder.log.5 ]] && rm /var/log/laundry_folder.log.5
[[ -f /var/log/laundry_folder.log.4 ]] && rmv /var/log/laundry_folder.log.4 /var/log/laundry_folder.log.5
[[ -f /var/log/laundry_folder.log.3 ]] && rmv /var/log/laundry_folder.log.3 /var/log/laundry_folder.log.4
[[ -f /var/log/laundry_folder.log.2 ]] && rmv /var/log/laundry_folder.log.2 /var/log/laundry_folder.log.3
[[ -f /var/log/laundry_folder.log.1 ]] && rmv /var/log/laundry_folder.log.1 /var/log/laundry_folder.log.2
[[ -f /var/log/laundry_folder.log ]] && rmv /var/log/laundry_folder.log /var/log/laundry_folder.log.1
echo "[$(date -Is)] Service started NOW" | tee -a /var/log/laundry_folder.log
while true; do
  aplay "${WAV_PATH}/prepare_laundry1.wav"
  echo "[$(date -Is)] Waiting for ${WAIT_BETWEEN_FOLDING_CYCLES} seconds before starting a folding cycle..." | tee -a /var/log/laundry_folder.log
  sleep ${WAIT_BETWEEN_FOLDING_CYCLES}
  # Fold right flap
  "${FOLDER_REALPATH}/move-servo.py" 0 0
  sleep ${SLEEP_AFTER_CLOSED}
  "${FOLDER_REALPATH}/move-servo.py" 0 155
  sleep ${SLEEP_BETWEEN_FLAPS}

  # Fold left flap
  "${FOLDER_REALPATH}/move-servo.py" 1 155
  sleep ${SLEEP_AFTER_CLOSED}
  "${FOLDER_REALPATH}/move-servo.py" 1 0
  sleep ${SLEEP_BETWEEN_FLAPS}

  # Fold bottom flap
  "${FOLDER_REALPATH}/move-servo.py" 2 155
  sleep ${SLEEP_AFTER_CLOSED}
  "${FOLDER_REALPATH}/move-servo.py" 2 0
  echo "[$(date -Is)] Folding cycle ended. Will start a new folding cycle momentarily..." | tee -a /var/log/laundry_folder.log
done
