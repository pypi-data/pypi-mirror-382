#!/usr/bin/env bash

PACKAGE_NAME="$1"
adb shell monkey -p "$PACKAGE_NAME" -c android.intent.category.LAUNCHER 1

exit