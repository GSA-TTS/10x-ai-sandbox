#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR" || exit

if [ -n "$VCAP_APPLICATION" ]; then
    echo "Running inside a Cloud Foundry instance, setting paths"
    export PATH="$HOME/deps/1/node/bin:$HOME/deps/0/bin:$PATH"
    export LD_LIBRARY_PATH="$HOME/deps/0/lib:$LD_LIBRARY_PATH"
    echo "PATH is set to: $PATH"
    echo "LD_LIBRARY_PATH is set to: $LD_LIBRARY_PATH"

    echo "===========//===========$(df -h)"

    # Clean npm cache
    echo "Cleaning npm cache..."
    npm cache clean --force

    # Clean Node.js cache if any (optional)
    echo "Cleaning Node.js cache..."
    if [ -d "$HOME/.node-gyp" ]; then
        rm -rf "$HOME/.node-gyp"
    fi

    if [ -d "$HOME/.npm" ]; then
        rm -rf "$HOME/.npm"
    fi

    if [ -d "$HOME/.cache/yarn" ]; then
        rm -rf "$HOME/.cache/yarn"
    fi

    # Install packages with temporary cache
    echo "Installing npm packages with temporary cache..."
    npm install --include=dev

    echo "===========//===========$(df -h)"

    npm run build

    echo "===========//===========$(df -h)"
else
    echo "Not running inside a Cloud Foundry instance. Skipping path setting."
fi

rm -rf node_modules
npm install --only=production --prefer-online

echo "===========//===========$(df -h)"

# Clean npm and Yarn caches
echo "Cleaning npm and Yarn caches..."
npm cache clean --force
yarn cache clean

# Clean output directory (dist)
echo "Cleaning Vite output directory..."
rm -rf dist

# Clean ESLint and Prettier caches
echo "Cleaning ESLint and Prettier caches..."
rm -f .eslintcache
rm -f .prettiercache

# Clean Babel cache
echo "Cleaning Babel cache..."
rm -rf .babel_cache

# Clean TypeScript cache
echo "Cleaning TypeScript cache..."
rm -f tsconfig.tsbuildinfo

# Clean any other potential caches related to Vite or build tools
echo "Cleaning .vite and other build caches..."
rm -rf .vite
rm -rf .cache

if [ -d "$HOME/.node-gyp" ]; then
    rm -rf "$HOME/.node-gyp"
fi

if [ -d "$HOME/.cache/yarn" ]; then
    rm -rf "$HOME/.cache/yarn"
fi

echo "All caches cleaned!"

echo "===========//===========$(df -h)"

pip3 install -r ./backend/requirements.txt --no-cache-dir

echo "===========//===========$(df -h)"

# pip3 install -r ./backend/open-webui-pipelines/requirements.txt --no-cache-dir

# echo "===========//===========$(df -h)"

# bash $SCRIPT_DIR/backend/start.sh
