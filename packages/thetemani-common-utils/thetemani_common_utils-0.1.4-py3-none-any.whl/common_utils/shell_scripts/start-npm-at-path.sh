#!/usr/bin/env bash

PATH_TO_DIRECTORY="$1"

cd "$PATH_TO_DIRECTORY" || {
    echo "Directory not found: $PATH_TO_DIRECTORY"
    exit 1
}
npm start &

exit
