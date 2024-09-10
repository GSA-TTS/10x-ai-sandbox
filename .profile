#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR" || exit

if [ -n "$VCAP_APPLICATION" ]; then
    echo "Running inside a Cloud Foundry instance, setting paths"
    # export PATH="$HOME/deps/1/node/bin:$HOME/deps/0/bin:$PATH"
    # export LD_LIBRARY_PATH="$HOME/deps/0/lib:$LD_LIBRARY_PATH"
    echo "PATH is set to: $PATH"
    echo "LD_LIBRARY_PATH is set to: $LD_LIBRARY_PATH"
    echo "Pip3 version: $(pip3 --version)"
    npm install --include=dev
    npm run build
else
    echo "Not running inside a Cloud Foundry instance. Skipping path setting."
fi

ln -sf $(which pip3) $HOME/bin/pip

bash $SCRIPT_DIR/backend/start.sh
