#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR" || exit

PORT="${PORT:-9099}"
PIDS=$(lsof -ti:$PORT)
if [ -n "$PIDS" ] ; then
    echo "$PIDS" | xargs kill -9
fi

uvicorn main:app --port $PORT --host 0.0.0.0 --forwarded-allow-ips '*' --reload
