#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR" || exit

if [ -n "$VCAP_APPLICATION" ]; then
    echo "Running inside a Cloud Foundry instance, setting paths"
    # export PATH="$HOME/deps/1/node/bin:$HOME/deps/0/bin:$PATH"
    # export PATH="$HOME/deps/0/python/bin:$PATH"
    # export LD_LIBRARY_PATH="$HOME/deps/0/lib:$LD_LIBRARY_PATH"

    # use apt buildpack to install ffmpeg instead
    # apt update
    # apt install -y ffmpeg

    function vcap_get_service() {
        local path name
        name="$1"
        path="$2"
        echo "$VCAP_SERVICES" | jq --raw-output --arg service_name "$name" ".[][] | select(.name == \$service_name) | $path"
    }

    # TKTK - The service name should be configurable
    export VCAP_SERVICE_NAME_AZURE_AI_GPT4O="azure-ai-gpt-4o"

    export endpoint_url=$(vcap_get_service $VCAP_SERVICE_NAME_AZURE_AI_GPT4O .credentials.endpoint_url)

    echo "endpoint_url is set to: $endpoint_url"

    function trim_url() {
        local trimmed_url=$(echo "$1" | sed 's/\/openai.*$//' | sed 's/\/$//')
        echo "$trimmed_url"
    }

    export AZURE_OPENAI_ENDPOINT=$(trim_url "$endpoint_url") 
    echo "AZURE_OPENAI_ENDPOINT is set to: $AZURE_OPENAI_ENDPOINT"  

    export AZURE_OPENAI_GPT4OMNI_DEPLOYMENT_NAME=$(vcap_get_service $VCAP_SERVICE_NAME_AZURE_AI_GPT4O .credentials.model_name)
    echo "AZURE_OPENAI_GPT4OMNI_DEPLOYMENT_NAME is set to: $AZURE_OPENAI_GPT4OMNI_DEPLOYMENT_NAME"

    export AZURE_OPENAI_API_KEY=$(vcap_get_service $VCAP_SERVICE_NAME_AZURE_AI_GPT4O .credentials.api_key)
    echo "AZURE_OPENAI_API_KEY is set to: $(echo $AZURE_OPENAI_API_KEY | sed 's/^\(....\).*$/\1****/')"

    echo "PATH is set to: $PATH"
    echo "LD_LIBRARY_PATH is set to: $LD_LIBRARY_PATH"

    NEW_PATH="/home/vcap/deps/0/python/bin"
    echo "New path to add: $NEW_PATH"
    # Check if the new path is already in the PATH variable
    if [[ ":$PATH:" != *":$NEW_PATH:"* ]]; then
        echo "Adding $NEW_PATH to PATH..."
        export PATH="$NEW_PATH:$PATH"
    fi
    echo "Current PATH is now: $PATH"

    echo "===========/startup/===========\n$(df -h | sed -n '2p')\n============================"

    echo "===========Skipping runtime pip and npm installs========"
fi
#     rm -rf node_modules
# 
#     # Clean npm cache
#     echo "Cleaning npm cache..."
#     npm cache clean --force
# 
#     # Clean Node.js cache if any (optional)
#     echo "Cleaning Node.js cache..."
#     if [ -d "$HOME/.node-gyp" ]; then
#         rm -rf "$HOME/.node-gyp"
#     fi
# 
#     if [ -d "$HOME/.npm" ]; then
#         rm -rf "$HOME/.npm"
#     fi
# 
#     if [ -d "$HOME/.cache/yarn" ]; then
#         rm -rf "$HOME/.cache/yarn"
#     fi
# 
#     # Install packages with temporary cache
#     echo "Installing npm packages with temporary cache..."
#     npm install --include=dev
# 
#     echo "===========/installed node dev deps/===========\n$(df -h | sed -n '2p')\n============================"
# 
#     npm run build
# 
#     echo "===========/build has run/===========\n$(df -h | sed -n '2p')"
# else
#     echo "Not running inside a Cloud Foundry instance. Skipping path setting."
# fi
# 
# rm -rf node_modules
# # npm install --only=production --prefer-online
# 
# # Clean npm and Yarn caches
# echo "Cleaning npm and Yarn caches..."
# npm cache clean --force
# yarn cache clean || true
# 
# echo "===========/remove modules, install prod, clean/===========\n$(df -h | sed -n '2p')"
# 
# # Clean output directory (dist)
# echo "Cleaning Vite output directory..."
# rm -rf dist || true
# 
# # Clean ESLint and Prettier caches
# echo "Cleaning ESLint and Prettier caches..."
# rm -f .eslintcache || true
# rm -f .prettiercache || true
# 
# # Clean Babel cache
# echo "Cleaning Babel cache..."
# rm -rf .babel_cache || true
# 
# # Clean TypeScript cache
# echo "Cleaning TypeScript cache..."
# rm -f tsconfig.tsbuildinfo || true
# 
# # Clean any other potential caches related to Vite or build tools
# echo "Cleaning .vite and other build caches..."
# rm -rf .vite || true
# rm -rf .cache || true
# 
# if [ -d "$HOME/.node-gyp" ]; then
#     rm -rf "$HOME/.node-gyp"
# fi
# 
# if [ -d "$HOME/.cache/yarn" ]; then
#     rm -rf "$HOME/.cache/yarn"
# fi
# 
# echo "All caches cleaned!"
# 
# echo "===========/node vite caches clean/===========\n$(df -h | sed -n '2p')"
# 
# export USE_CUDA=0
# export USE_CUDNN=0
# export USE_MKLDNN=0
# export USE_NCCL=0
# export USE_DISTRIBUTED=0
# export USE_QNNPACK=0
# export BUILD_TEST=0
# 
# echo "Clearing pip cache..."
# pip3 cache purge
# df -h | sed -n '2p'
# 
# echo "Installing torch"
# # pip3 install torch==2.4.1 --no-cache-dir
# pip3 install torch --index-url https://download.pytorch.org/whl/cpu
# # pip3 install torch==2.4.1 --extra-index-url https://download.pytorch.org/whl/cpu
# 
# echo "Clearing pip cache..."
# pip3 cache purge
# echo "Disk usage after installing torch:"
# df -h | sed -n '2p'
# 
# echo "pip show torch: $(pip3 show torch)"
# 
# echo "===========/install requirements.txt/===========\n$(df -h | sed -n '2p')"
# 
# # Read requirements.txt file line by line
# while IFS= read -r package || [[ -n "$package" ]]; do
#     # Skip empty lines and comments
#     if [[ -z "$package" || "$package" == \#* ]]; then
#         continue
#     fi
# 
#     # Install the package
#     echo "Installing $package..."
#     pip3 install "$package"
# 
#     # Clear pip cache to free up disk space
#     echo "Clearing pip cache..."
#     pip3 cache purge
# 
#     # Display the current disk usage
#     echo "Disk usage after installing $package:"
#     df -h | sed -n '2p'
# 
#     echo
# 
# done <"./backend/requirements.txt"
# 
# echo "All packages installed."
# 
# echo "===========/installed backend reqs/===========\n$(df -h | sed -n '2p')"
# 
# # bash $SCRIPT_DIR/backend/start.sh
