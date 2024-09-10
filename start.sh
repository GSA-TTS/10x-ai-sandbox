#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR" || exit

# Check if the environment variable VCAP_APPLICATION exists
if [ -n "$VCAP_APPLICATION" ]; then
    echo "Running inside a Cloud Foundry instance, setting paths"
    # Add Node.js and Python paths
    export PATH="$HOME/deps/1/node/bin:$HOME/deps/0/bin:$PATH"
    # Set the library path for Python
    export LD_LIBRARY_PATH="$HOME/deps/0/lib:$LD_LIBRARY_PATH"
    # Echo the paths to verify when you SSH in
    echo "PATH is set to: $PATH"
    echo "LD_LIBRARY_PATH is set to: $LD_LIBRARY_PATH"
else
    echo "Not running inside a Cloud Foundry instance. Skipping path setting."
fi

npm run build

bash $SCRIPT_DIR/backend/start.sh
