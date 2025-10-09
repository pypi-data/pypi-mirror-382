#!/usr/bin/env bash

DEVICE_ID="$1"
/opt/genymobile/genymotion/player --vm-name "$DEVICE_ID" &

while ! adb shell getprop sys.boot_completed | grep -m 1 '1'; do
  sleep 1
done

exit
