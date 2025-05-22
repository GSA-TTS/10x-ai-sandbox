#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR" || exit

PORT="${PORT:-8080}"
PIDS=$(lsof -ti:$PORT)
if [ -n "$PIDS" ] ; then
    echo "$PIDS" | xargs kill -9
fi

uvicorn open_webui.main:app --port $PORT --host 0.0.0.0 --forwarded-allow-ips '*' --reload
