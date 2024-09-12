#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR" || exit

if [ -n "$VCAP_APPLICATION" ]; then
    echo "Running inside a Cloud Foundry instance, setting paths"
    echo "PATH is set to: $PATH"
    echo "LD_LIBRARY_PATH is set to: $LD_LIBRARY_PATH"
else
    echo "Not running inside a Cloud Foundry instance."
fi

bash $SCRIPT_DIR/backend/start.sh
