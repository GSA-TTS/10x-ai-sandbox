#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR" || exit

bash $SCRIPT_DIR/open-webui-pipelines/start.sh &

# REQUIREMENTS_PATH=$SCRIPT_DIR/requirements.txt

# Function to install requirements if requirements.txt is provided
install_requirements() {
  if [[ -f "$1" ]]; then
    echo "requirements.txt found at $1. Installing requirements..."
    pip3 install -r "$1"
  else
    echo "requirements.txt not found at $1. Skipping installation of requirements."
  fi
}

# Check if the REQUIREMENTS_PATH environment variable is set and non-empty
if [[ -n "$REQUIREMENTS_PATH" ]]; then
  # Install requirements from the specified requirements.txt
  install_requirements "$REQUIREMENTS_PATH"
else
  echo "REQUIREMENTS_PATH not specified. Skipping installation of requirements."
fi

KEY_FILE=.webui_secret_key

PORT="${PORT:-8080}"
HOST="${HOST:-0.0.0.0}"
if test "$WEBUI_SECRET_KEY $WEBUI_JWT_SECRET_KEY" = " "; then
  echo "Loading WEBUI_SECRET_KEY from file, not provided as an environment variable."

  if ! [ -e "$KEY_FILE" ]; then
    echo "Generating WEBUI_SECRET_KEY"
    # Generate a random value to use as a WEBUI_SECRET_KEY in case the user didn't provide one.
    echo $(head -c 12 /dev/random | base64) >"$KEY_FILE"
  fi

  echo "Loading WEBUI_SECRET_KEY from $KEY_FILE"
  WEBUI_SECRET_KEY=$(cat "$KEY_FILE")
fi

# if [[ "${USE_OLLAMA_DOCKER,,}" == "true" ]]; then
#   echo "USE_OLLAMA is set to true, starting ollama serve."
#   ollama serve &
# fi

# if [[ "${USE_CUDA_DOCKER,,}" == "true" ]]; then
#   echo "CUDA is enabled, appending LD_LIBRARY_PATH to include torch/cudnn & cublas libraries."
#   export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib/python3.11/site-packages/torch/lib:/usr/local/lib/python3.11/site-packages/nvidia/cudnn/lib"
# fi

if [ -n "$VCAP_APPLICATION" ]; then
  WEBUI_SECRET_KEY="$WEBUI_SECRET_KEY" exec uvicorn main:app --host "$HOST" --port "$PORT" --forwarded-allow-ips '*'
else
  echo "Not running inside a Cloud Foundry instance."
  WEBUI_SECRET_KEY="$WEBUI_SECRET_KEY" exec uvicorn main:app --port $PORT --host 0.0.0.0 --forwarded-allow-ips '*' --reload
fi
