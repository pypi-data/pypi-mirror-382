#!/usr/bin/env bash

if [ -z "$1" ]; then
    echo "Usage: $0 <port>"
    exit 1
fi

PORT=$1

PID=$(lsof -t -i:$PORT)

if [ -z "$PID" ]; then
    echo "No process found on port $PORT."
    exit 1
fi

kill -9 $PID

if [ $? -eq 0 ]; then
    echo "Process on port $PORT (PID $PID) has been terminated."
else
    echo "Failed to terminate the process on port $PORT."
fi
