#!/usr/bin/env bash

if [ -z "$1" ]; then
    echo "Usage: $0 <URL>"
    exit 1
fi

URL="$1"

firefox "$URL" &

exit 0
